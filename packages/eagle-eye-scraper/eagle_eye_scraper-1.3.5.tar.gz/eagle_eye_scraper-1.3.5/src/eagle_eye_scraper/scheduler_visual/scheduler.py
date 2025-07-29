import logging

from apscheduler.events import *
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from eagle_eye_scraper.com.utils.time_util import TimeUtils

logger = logging.getLogger()

jobstores = {"default": MemoryJobStore()}
executors = {"default": ThreadPoolExecutor(30)}
job_defaults = {"misfire_grace_time": 10, "coalesce": True, "max_instances": 1}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults,
                                timezone=TimeUtils.shanghai_tz, jobstore_retry_interval=10, logger=logger)

event_listeners = {
    EVENT_EXECUTOR_ADDED: ("Add executor", executors),
    EVENT_EXECUTOR_REMOVED: ("Remove executor", executors),
    EVENT_JOBSTORE_ADDED: ("Add job store", jobstores),
    EVENT_JOBSTORE_REMOVED: ("Remove job store", jobstores),
    EVENT_JOB_ADDED: ("Add job", None),
    EVENT_JOB_REMOVED: ("Remove job", None),
    EVENT_JOB_MODIFIED: ("Modify job", None),
    EVENT_JOB_EXECUTED: ("Executed job", None),
    EVENT_JOB_ERROR: ("Error job", None),
    EVENT_JOB_MISSED: ("Missed job", None),
    EVENT_JOB_SUBMITTED: ("Submit job", None),
}


def listen_event(event: SchedulerEvent, mapper: dict, action: str):
    obj = f"{event.alias}[{mapper.get(event.alias, 'Unknown')}]"
    logger.debug(f"{action} {obj}")


def listen_job_event(event: JobEvent, action: str):
    job = scheduler.get_job(event.job_id)
    logger.debug(f"{action}: {job.name if job else 'Unknown'} [{event.job_id}]")


def listen_job_execution_event(event: JobExecutionEvent, action: str):
    job_info = scheduler.get_job(event.job_id)
    message = f"{action}: {event.job_id} [{job_info}]"
    if event.exception:
        logger.error(message, exc_info=True)
    else:
        logger.debug(message)


def listen_job_submission_event(event: JobSubmissionEvent):
    job = scheduler.get_job(event.job_id)
    if job:
        logger.debug(f"Submit job: {job.name} [{event.job_id}], next run at {job.next_run_time}")


def event_listener(event):
    action, mapper = event_listeners.get(event.code, (None, None))
    if action:
        (listen_event if mapper else listen_job_event)(event, action=action)


scheduler.add_listener(event_listener)


logger.info(f" scheduler executor: {scheduler._executors}")
logger.info(f" scheduler jobstores: {scheduler._jobstores}")
