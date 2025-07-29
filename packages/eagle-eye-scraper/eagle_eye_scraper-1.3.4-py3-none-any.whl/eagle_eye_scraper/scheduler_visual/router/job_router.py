import json
import logging
from importlib import import_module, reload
from pathlib import Path
from typing import Literal

from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, Request
from fastui import FastUI
from fastui import components as c
from fastui.base import BaseModel
from fastui.components.display import DisplayLookup
from fastui.events import PageEvent, GoToEvent, BackEvent
from fastui.forms import fastui_form

from eagle_eye_scraper.com.utils.string_utils import removesuffix
from eagle_eye_scraper.com.utils.time_util import TimeUtils
from eagle_eye_scraper.dispatch.host_dispatcher import HostDispatchExecutor
from eagle_eye_scraper.scheduler_visual.schema import JobInfo, NewJobParam, ModifyJobParam
from eagle_eye_scraper.scheduler_visual.shared import frame_page, confirm_modal

logger = logging.getLogger()


class SpiderJobItem(BaseModel):
    crom_expr: str
    spider_class: str
    spider_func: str
    func_kwargs: dict = None


def edit_job_script(path: Path):
    if not path.exists():
        return c.Error(title="Error", description=f"Module {path} not found", status_code=500)
    return c.Code(text=path.read_text(), language="python")


def serialize_job_data(scheduler, job: Job):
    data = {name: getattr(job, name, None) for name in job.__slots__}
    executor = job.executor
    executor_class = scheduler._executors[executor].__class__
    data["executor"] = f"{executor_class.__name__}({executor})"

    job_store = job._jobstore_alias
    job_store_class = scheduler._jobstores[job_store].__class__
    data["jobstore"] = f"{job_store_class.__name__}({job_store})"

    data["func"] = f"{job.func.__module__}.{job.func.__qualname__}"
    data["args"] = json.dumps(job.args)
    data["kwargs"] = json.dumps(job.kwargs)
    data["trigger"] = removesuffix(job.trigger.__class__.__name__, "Trigger")
    data["trigger_params"] = job.trigger

    return data


async def jobs(request: Request):
    scheduler = request.app.state.scheduler
    logger.debug("call /job/")
    jobs = scheduler.get_jobs()

    job_info_list = []
    for job in jobs:
        data = serialize_job_data(scheduler, job)
        job_info_list.append(JobInfo(**data))

    return frame_page(
        c.Heading(text="Job"),
        c.Table(
            data=job_info_list,
            data_model=JobInfo,
            columns=[
                DisplayLookup(field="id", on_click=GoToEvent(url="/detail/{id}")),
                DisplayLookup(field="name"),
                DisplayLookup(field="executor"),
                DisplayLookup(field="trigger"),
                DisplayLookup(field="next_run_time"),
            ],
        ),
    )


async def new_job(request: Request, job_info: NewJobParam = fastui_form(NewJobParam)):
    scheduler = request.app.state.scheduler
    trigger = job_info.get_trigger()
    job = scheduler.add_job(
        job_info.func,
        trigger=trigger,
        args=job_info.args,
        kwargs=job_info.kwargs,
        coalesce=job_info.coalesce,
        max_instances=job_info.max_instances,
        misfire_grace_time=job_info.misfire_grace_time,
        name=job_info.name,
        id=job_info.id,
        executor=job_info.executor,
        jobstore=job_info.jobstore,
    )
    return [
        c.Paragraph(text=f"Created new job(id={job.id})"),
        # TODO: GotoEvent will not refresh the page
        c.Button(text="Back Home", on_click=GoToEvent(url="/")),
    ]


async def job_detail(request: Request, id: str):
    scheduler = request.app.state.scheduler
    job = scheduler.get_job(id)
    if not job:
        return [c.FireEvent(event=GoToEvent(url="/"))]
    data = serialize_job_data(scheduler, job)
    job_model = JobInfo(**data)
    path = Path(*job.func.__module__.split(".")).with_suffix(".py")
    return frame_page(
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Heading(text="Job Detail"),
        c.Div(
            components=[
                # confirm model will be triggered by the underscored title of the modal
                c.Button(
                    text="View Script",
                    on_click=PageEvent(name="view", next_event=PageEvent(name="load-script")),
                    named_style="secondary",
                ),
                c.Modal(
                    title=str(path),
                    body=[
                        c.ServerLoad(
                            path=f"/view/{path}", load_trigger=PageEvent(name="load-script")
                        )
                    ],
                    open_trigger=PageEvent(name="view"),
                    class_name="modal-xl",
                ),
                c.Button(text="Pause", on_click=PageEvent(name="pause_job")),
                confirm_modal(title="Pause Job", submit_url=f"/pause/{id}"),
                c.Button(text="Resume", on_click=PageEvent(name="resume_job")),
                confirm_modal(title="Resume Job", submit_url=f"/resume/{id}"),
                c.Button(text="Modify", on_click=PageEvent(name="modify_job")),
                c.Modal(
                    title="Modify Job",
                    body=[
                        c.ModelForm(
                            submit_url=f"/job/modify/{id}",
                            model=JobInfo,
                            initial=job_model.model_dump(exclude_defaults=True),
                        )
                    ],
                    open_trigger=PageEvent(name="modify_job"),
                ),
                c.Button(text="Reload", on_click=PageEvent(name="reload_job")),
                confirm_modal(title="Reload Job", submit_url=f"/reload/{id}"),
                c.Button(
                    text="Remove", on_click=PageEvent(name="remove_job"), named_style="warning"
                ),
                confirm_modal(title="Remove Job", submit_url=f"/remove/{id}"),
            ],
            class_name="d-flex flex-start gap-3 mb-3",
        ),
        c.Details(data=job_model),
    )


async def modify_job(request: Request, id: str, job_info: ModifyJobParam = fastui_form(ModifyJobParam)):
    scheduler = request.app.state.scheduler
    modify_kwargs = job_info.model_dump(exclude={"trigger", "trigger_params"})
    modify_kwargs["trigger"] = job_info.get_trigger()
    modify_kwargs = dict(filter(lambda x: x[1], modify_kwargs.items()))
    scheduler.modify_job(id, **modify_kwargs)

    return [
        c.Paragraph(text="Job config after modified"),
        c.Json(
            value=modify_kwargs | {"trigger": job_info.trigger, "trigger_params": job_info.trigger_params}
        ),
        c.Button(text="Back Home", on_click=GoToEvent(url="/")),
    ]


async def pause_job(request: Request, action: Literal["pause", "resume", "modify", "reload", "remove"], id: str):
    scheduler = request.app.state.scheduler
    job = scheduler.get_job(id)
    if not job:
        return c.Error(title="Error", description=f"Job({id=}) not found", status_code=500)

    if action == "pause":
        scheduler.pause_job(id)
    elif action == "resume":
        scheduler.resume_job(id)
    elif action == "remove":
        scheduler.remove_job(id)
    elif action == "reload":
        module = import_module(job.func.__module__)
        reload(module)
    else:
        raise ValueError(f"Invalid action {action}")

    return [
        c.Paragraph(text=f"Job({id=}, name='{job.name}'), {action=} success."),
        c.Button(text="Back Home", on_click=GoToEvent(url="/")),
    ]


async def new_spider_job(request: Request, item: SpiderJobItem):
    scheduler = request.app.state.scheduler
    success = True
    try:
        logger.info(f"spider job item: {item}")
        host_dispatch_executor = HostDispatchExecutor()
        trigger = CronTrigger.from_crontab(item.crom_expr, timezone=TimeUtils.shanghai_tz)
        scheduler.add_job(trigger=trigger,
                          name=f"{item.spider_class}::{item.spider_func}",
                          func=host_dispatch_executor.call_executor,
                          args=(item.spider_class, item.spider_func,),
                          kwargs=item.func_kwargs,
                          coalesce=True,
                          max_instances=1,
                          misfire_grace_time=30)
    except Exception:
        success = False
        logger.error("创建spider-job失败：", exc_info=True)
    return {"success": success}


router = APIRouter(prefix="/job", tags=["job"])

router.add_api_route(
    path="/",
    endpoint=jobs,
    methods=["GET"],
    response_model=FastUI,
    response_model_exclude_none=True
)

router.add_api_route(
    path="/",
    endpoint=new_job,
    methods=["POST"],
    response_model=FastUI,
    response_model_exclude_none=True
)

router.add_api_route(
    path="/new/spider",
    endpoint=new_spider_job,
    methods=["POST"]
)

router.add_api_route(
    path="/detail/{id}",
    endpoint=job_detail,
    methods=["GET"],
    response_model=FastUI,
    response_model_exclude_none=True
)

router.add_api_route(
    path="/modify/{id}",
    endpoint=modify_job,
    methods=["POST"],
    response_model=FastUI,
    response_model_exclude_none=True
)

router.add_api_route(
    path="/{action}/{id}",
    endpoint=pause_job,
    methods=["POST"],
    response_model=FastUI,
    response_model_exclude_none=True
)

router.add_api_route(
    path="/view/{path:path}",
    endpoint=edit_job_script,
    methods=["GET"],
    response_model=FastUI,
    response_model_exclude_none=True
)
