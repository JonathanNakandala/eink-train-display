"""
FastAPI for:
    - Generating Image
    - Scheduling Image Generation
    - Sending Image to Display
"""
import asyncio
from contextlib import asynccontextmanager
import datetime
import structlog
from fastapi import FastAPI
import uvicorn
from .log_setup import setup_logging

from .utils import run_dashboard_update
from .routers import schedule
from .dependencies import Scheduler, get_apiconfig

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    """
    FastAPI Startup/Shutdown
    """
    api_config = get_apiconfig()
    fast_app.state.scheduler = Scheduler()
    fast_app.state.scheduler.scheduler.add_job(
        run_dashboard_update,
        "interval",
        args=[api_config],
        seconds=5 * 60,  # 5 minutes
        next_run_time=datetime.datetime.now(),
    )
    fast_app.state.scheduler.scheduler.start()

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(schedule.router)


def start_uvicorn(async_loop: asyncio.AbstractEventLoop):
    """
    Start Server
    """
    config = uvicorn.Config(app, loop=loop)
    server = uvicorn.Server(config)
    async_loop.run_until_complete(server.serve())


if __name__ == "__main__":
    setup_logging()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_uvicorn(loop)
