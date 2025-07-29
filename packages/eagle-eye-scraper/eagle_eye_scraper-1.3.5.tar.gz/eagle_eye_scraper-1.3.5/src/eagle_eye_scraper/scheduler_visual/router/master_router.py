import logging
from importlib import import_module

from fastapi import APIRouter, Request
from fastui.forms import SelectSearchResponse
from fastui.json_schema import SelectOption

from eagle_eye_scraper import CONFIG

logger = logging.getLogger()

router = APIRouter(prefix="/api", tags=["job"])


def get_job_stores(request: Request) -> SelectSearchResponse:
    scheduler = request.app.state.scheduler
    stores = [
        SelectOption(value=name, label=f"{name}({store.__class__.__name__})")
        for name, store in scheduler._jobstores.items()
    ]
    return SelectSearchResponse(options=stores)


def get_executors(request: Request) -> SelectSearchResponse:
    scheduler = request.app.state.scheduler
    executors = [
        SelectOption(value=name, label=f"{name}({executor.__class__.__name__})")
        for name, executor in scheduler._executors.items()
    ]
    return SelectSearchResponse(options=executors)


def get_available_job_stores() -> SelectSearchResponse:
    stores = [SelectOption(value="Memory", label="Memory")]
    for store in ["MongoDB", "Redis", "SQLAlchemy"]:
        try:
            import_module(f"apscheduler.jobstores.{store.lower()}")
            stores.append(SelectOption(value=store, label=f"{store}JobStore"))
        except ImportError as e:
            print(e)

    return SelectSearchResponse(options=stores)


def get_available_job_logs(q: str = "") -> SelectSearchResponse:
    logs = [
        SelectOption(value=file.name, label=file.name)
        for file in sorted(CONFIG.LOG_PATH.iterdir(), reverse=True)
        if file.suffix == ".log" and file.name.startswith("jobs") and q in file.name
    ]
    return SelectSearchResponse(options=logs)


router.add_api_route(
    path="/job-stores",
    endpoint=get_job_stores,
    methods=["GET"],
    description="Get job stores"
)

router.add_api_route(
    path="/executors",
    endpoint=get_executors,
    methods=["GET"],
    description="Get executors"
)

router.add_api_route(
    path="/available-job-stores",
    endpoint=get_available_job_stores,
    methods=["GET"],
    description="Get available job stores"
)

router.add_api_route(
    path="/available-logs",
    endpoint=get_available_job_logs,
    methods=["GET"],
    description="Get available log file"
)
