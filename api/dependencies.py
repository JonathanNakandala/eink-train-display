"""
API config
"""
import functools
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from fastapi import Request
import structlog
from api.config import load_config, ConfigVars

log = structlog.get_logger()


class Scheduler:
    """
    Class for Dependency Injection
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()


def get_scheduler(request: Request) -> AsyncIOScheduler:
    """
    Get scheduler function
    """
    return request.app.state.scheduler.scheduler


class APIConfig:
    """
    Singleton for API Configuration
    """

    _instance = None
    update_interval: datetime.timedelta = datetime.timedelta(minutes=5)
    job = None

    @functools.lru_cache(None)  # pylint: disable=method-cache-max-size-none
    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        return super(APIConfig, cls).__new__(cls)

    def __init__(self):
        """
        Create Scheduler
        """
        self.config: ConfigVars = load_config()

    def set_job(self, job: Job):
        """
        Sets the job scheduled in the BackgroundScheduler.
        """
        log.info("Setting Job", job=job)
        self.job = job

    def update_now(self, request: Request):
        """
        Update the dashboard now
        """

        scheduler = get_scheduler(request)
        jobs = scheduler.get_jobs()
        log.debug("Searching for Jobs", jobs=jobs, type=type(jobs))

        for job in jobs:
            if job.name == "run_dashboard_update":
                log.info("Modifying the job", id=job.id, name=job.name)
                job = scheduler.modify_job(
                    job.id, next_run_time=datetime.datetime.now()
                )
                break

    def reschedule(self, request: Request, new_interval: datetime.timedelta):
        """
        Reschedules the job with a new interval.
        """
        log.info(
            "Rescheduling job interval",
            old_interval=self.update_interval,
            new_interval=new_interval,
        )
        scheduler = get_scheduler(request)

        for job in scheduler.get_jobs():
            if job.name == "run_dashboard_update":
                scheduler.reschedule_job(
                    job.id, trigger="interval", seconds=new_interval.total_seconds()
                )
                log.info("Job Modified", job_id=job.id, next_run=job.next_run_time)
                self.update_interval = new_interval
                break
        else:
            log.warning("Job not found")


def get_apiconfig():
    """
    Returns APIConfig for use in Depends
    """
    return APIConfig()
