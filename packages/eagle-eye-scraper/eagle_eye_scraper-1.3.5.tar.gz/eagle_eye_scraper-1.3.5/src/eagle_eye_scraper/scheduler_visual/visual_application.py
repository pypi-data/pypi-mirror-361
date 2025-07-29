import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastui import prebuilt_html
from starlette.responses import HTMLResponse

from eagle_eye_scraper.scheduler_visual.router.executor_router import router as executor_router
from eagle_eye_scraper.scheduler_visual.router.job_router import router as job_router
from eagle_eye_scraper.scheduler_visual.router.log_router import router as log_router
from eagle_eye_scraper.scheduler_visual.router.master_router import router as master_router
from eagle_eye_scraper.scheduler_visual.router.stores_router import router as stores_router
from eagle_eye_scraper.scheduler_visual.scheduler import scheduler

logger = logging.getLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.scheduler = scheduler
    logger.info("注入scheduler")
    try:
        app.state.scheduler.start()
        yield
    finally:
        app.state.scheduler.shutdown()
        logger.info("Scheduler stopped.")


visual_app = FastAPI(title="Scraper Dispatch Scheduler Web Visual", lifespan=lifespan)

visual_app.include_router(master_router)
visual_app.include_router(executor_router)
visual_app.include_router(job_router)
visual_app.include_router(log_router)
visual_app.include_router(stores_router)


@visual_app.get("/")
def index() -> HTMLResponse:
    logger.debug("Load index")
    return HTMLResponse(prebuilt_html(api_root_url="/job"))


def run_app(port=9000):
    logger.info(f"Scheduler visualization running at: http://127.0.0.1:{port}")
    uvicorn.run(visual_app, host="0.0.0.0", port=port, log_level="debug")
