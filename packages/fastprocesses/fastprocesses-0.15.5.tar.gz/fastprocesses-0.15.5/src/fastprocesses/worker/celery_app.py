# worker/celery_app.py
import json
from datetime import datetime, timezone
import signal
import traceback
from typing import Any, Dict

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError

from fastprocesses.common import (
    celery_app, job_status_cache, sigint_handler, sigterm_handler,
    temp_result_cache
)
from fastprocesses.core.exceptions import (
    InputValidationError, ProcessClassNotFoundError
)
from fastprocesses.core.logging import logger
from fastprocesses.core.models import (
    CalculationTask,
    JobStatusCode,
    JobStatusInfo,
    Link,
)
from fastprocesses.processes.process_registry import get_process_registry

# NOTE: Cache hash key is based on original unprocessed inputs always
# this ensures consistent caching and cache retrieval
# which does not depend on arbitrary processed data, which can change
# when the process is updated or changed!

# Register signal handlers
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigint_handler)

class CacheResultTask(Task):
    def on_success(self, retval: dict | BaseModel, task_id, args, kwargs):
        try:
            # Deserialize the original data
            original_data = json.loads(args[1])
            calculation_task = CalculationTask(**original_data)

            # Get the the hash key for the task
            key = calculation_task.celery_key

            # Store the result in cache
            # Use the task ID as the key
            serialized_result = temp_result_cache.put(key=key, value=retval)

            # TODO: shorten retval log!
            logger.info(
                f"Saved result with key {key} to cache: {serialized_result[:80]}"
            )
        except Exception as e:
            logger.error(f"Error caching results: {e}")


# Create a progress update function that captures the job_id
def update_job_status(
    job_id: str,
    progress: int,
    message: str | None = None,
    status: str | None = None,
    started: datetime | None = None,
) -> None:
    """
    Updates the progress of a job.

    Args:
        progress (int): The progress percentage (0-100).
        message (str): A message describing the current progress.
        status (str | None): The current status (e.g., "RUNNING", "SUCCESSFUL").
    """

    job_key = f"job:{job_id}"
    job_info = JobStatusInfo.model_validate(job_status_cache.get(job_key))

    job_info.status = status or job_info.status
    job_info.progress = progress
    job_info.started = started or job_info.started
    job_info.updated = datetime.now(timezone.utc)

    if status == JobStatusCode.SUCCESSFUL:
        job_info.finished = datetime.now(timezone.utc)
        job_info.links.append(
            Link.model_validate(
                {
                    "href": f"/jobs/{job_info.jobID}/results",
                    "rel": "results",
                    "type": "application/json",
                }
            )
        )

    if message:
        job_info.message = message

    job_status_cache.put(job_key, job_info)
    logger.debug(f"Updated progress for job {job_id}: {progress}%, {message}")


@celery_app.task(bind=True, name="fastprocesses.execute_process", base=CacheResultTask)
def execute_process(self, process_id: str, serialized_data: str | bytes):
    def job_progress_callback(progress: int, message: str | None = None):
        """
        Updates the progress of a job.

        Args:
            progress (int): The progress percentage (0-100).
            message (str): A message describing the current progress.
            status (str | None): The current status (e.g., "RUNNING", "SUCCESSFUL").
        """

        job_key = f"job:{job_id}"
        # TODO: job disappears(!) when progress is not between 0 and 100
        job_info = JobStatusInfo.model_validate(job_status_cache.get(job_key))

        job_info.progress = progress
        job_info.updated = datetime.now(timezone.utc)

        if message:
            job_info.message = message

        job_status_cache.put(job_key, job_info)
        logger.debug(f"Updated progress for job {job_id}: {progress}%, {message}")

    result = None
    job_status = JobStatusCode.RUNNING
    job_message = ""
    data: dict = json.loads(serialized_data)

    logger.info(f"Executing process {process_id} with data {serialized_data[:80]}")
    job_id = self.request.id  # Get the task/job ID
    

    # First: Get the process
    try:
        logger.info(f"Worker retrieving process {process_id} from registry")
        service = get_process_registry().get_process(process_id)
    except ValueError as e:
        job_status = JobStatusCode.FAILED
        update_job_status(
            job_id,
            0,
            f"Process '{process_id}' not found.",
            job_status,
        )
        raise e
    except ProcessClassNotFoundError as e:
        raise e

    # Second: deep validation of inputs
    try:
        logger.info(f"Worker validating inputs for process {process_id}")
        update_job_status(
            job_id,
            0,
            "Validating inputs. This may take a while for complex inputs.",
            job_status,
        )
        service.validate_inputs(data["inputs"])
    except ValueError as e:
        logger.error(f"Input validation failed for process {process_id}: {str(e)}")
        job_status = JobStatusCode.FAILED
        update_job_status(
            job_id,
            0,
            str(e),
            job_status,
        )
        raise InputValidationError(process_id, repr(e))

    # Third: Execute the process
    try:
        logger.info(f"Worker executing process {process_id} with data {data}")
        job_status = JobStatusCode.RUNNING
        update_job_status(
            job_id,
            0,
            "Process started",
            job_status,
            started=datetime.now(timezone.utc),
        )
        result = service.run_execute(
            data, job_progress_callback=job_progress_callback
        )

    except SoftTimeLimitExceeded as e:
        logger.warning(f"Task {job_id} hit the soft time limit: {e}")
        # Attempt to resume the process
        try:
            
            result = service.run_execute(
                data, job_progress_callback=job_progress_callback
            )

        except Exception as inner_exception:
            logger.error(
                f"Error while completing task after soft time limit: {inner_exception}"
            )

            raise e

        logger.info(f"Process {process_id} completed after soft time limit")
        job_status=JobStatusCode.SUCCESSFUL,

    # intercept all errors coming from the process` execution method
    except Exception as e:
        # Update job with error status
        job_status = JobStatusCode.FAILED

        # decide if its a validation error or a general error
        if isinstance(e, ValueError) or isinstance(e, ValidationError):
            logger.error(f"Validation error in process {process_id}: {e}")
            job_message = e
            raise e
        
        # get exception traceback for logging, in other cases 
        # (hiding app interna for security reasons)
        user_frame = traceback.TracebackException.from_exception(e).stack

        logger.exception(str(e), exc_info=True)

        job_message = (
            f"Error in {service.__class__.__name__}.{user_frame[-1].name} "
            f"line: '{user_frame[-1].line}' (lineno: {user_frame[-1].lineno})"
        )

        # this information will be written to celery job 
        # results and thus to /job/{job_id}/results
        raise Exception(
            job_message
        )

    finally:
        if result:
            result_dump = jsonable_encoder(result)
            logger.info(
                f"Process {process_id} executed "
                f"successfully with result {json.dumps(result_dump)[:80]}"
            )
            job_status = JobStatusCode.SUCCESSFUL

            # Mark job as complete
            update_job_status(
                job_id, 100,
                "Process completed",
                job_status
            )

            # Return from the finally block (this will exit the function)
            return result.model_dump(exclude_none=True)
        
        else:
            job_status = JobStatusCode.FAILED
            # Update job status for failed jobs that didn't raise exceptions
            update_job_status(
                job_id,
                0,
                str(job_message),
                job_status
            )
    
    logger.info(
        f"Process {service.__class__.__name__} execution completed. No result returned"
    )
    return None

@celery_app.task(name="fastprocesses.check_cache")
def check_cache(calculation_task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if results exist in cache and return status
    """
    task = CalculationTask(**calculation_task)
    cached_result = temp_result_cache.get(key=task.celery_key)

    if cached_result:
        logger.info(f"Cache hit for key {task.celery_key}")
        return {"status": "HIT", "result": cached_result}

    logger.info(f"Cache miss for key {task.celery_key}")
    return {"status": "MISS"}


@celery_app.task(bind=True, name="fastprocesses.find_result_in_cache")
def find_result_in_cache(self, celery_key: str) -> dict | None:
    """
    Retrieve result from cache
    """
    result = temp_result_cache.get(key=celery_key)
    if result:
        logger.info(f"Retrieved result from cache for key {celery_key}")
        update_job_status(
            job_id=self.request.id,
            progress=100,
            message="Result retrieved from cache.",
            status=JobStatusCode.SUCCESSFUL,
        )
    return result


# @task_failure.connect(sender=execute_process)
# def handle_execute_failure(
#     sender=None,
#     task_id=None,
#     exception=None,
#     traceback=None,
#     **kwargs
# ):
#     logger.error(
#         f"Task {task_id} failed. "
#         f"{repr(exception)}"
#         f"\nTraceback:\n{traceback}"
#     )
