import logging

from fastapi import APIRouter, Form, Request
from fastui import FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.components.forms import FormFieldInput
from fastui.events import PageEvent
from fastui.forms import fastui_form

from eagle_eye_scraper.scheduler_visual.schema import ExecutorInfo
from eagle_eye_scraper.scheduler_visual.shared import frame_page

logger = logging.getLogger()


def store_exec(request: Request):
    scheduler = request.app.state.scheduler
    executors = []
    for alias, executor in scheduler._executors.items():
        executors.append(ExecutorInfo(**{"alias": alias, "executor": executor}))

    return frame_page(
        c.Heading(text="Executor"),
        c.Div(
            components=[
                c.Button(text="New Executor", on_click=PageEvent(name="new_executor")),
                c.Modal(
                    title="New Job Executor",
                    body=[c.ModelForm(submit_url="/job/executor/new", model=ExecutorInfo)],
                    open_trigger=PageEvent(name="new_executor"),
                ),
                c.Button(
                    text="Remove Executor",
                    on_click=PageEvent(name="remove_executor"),
                    named_style="warning",
                ),
                c.Modal(
                    title="Remove Executor",
                    body=[
                        c.Form(
                            form_fields=[
                                FormFieldInput(name="alias", title="Alias", required=True)
                            ],
                            submit_url="/job/executor/remove",
                        )
                    ],
                    open_trigger=PageEvent(name="remove_executor"),
                ),
            ],
            class_name="d-flex flex-start gap-3 mb-3",
        ),
        c.Table(
            data=executors,
            data_model=ExecutorInfo,
            columns=[
                DisplayLookup(field="alias", table_width_percent=20),
                DisplayLookup(field="type_", table_width_percent=20),
                DisplayLookup(field="max_worker"),
            ],
        ),
    )


async def new_executor(request: Request, new_executor: ExecutorInfo = fastui_form(ExecutorInfo)):
    scheduler = request.app.state.scheduler
    alias = new_executor.alias
    if new_executor.alias in scheduler._jobstores:
        return c.Paragraph(text=f"Executor({alias=}) already exists.")
    executor = new_executor.get_executor()
    scheduler.add_executor(executor, alias=new_executor.alias)
    return c.Paragraph(text=f"New executor({alias=}) added successfully.")


async def remove_executor(request: Request, alias: str = Form()):
    scheduler = request.app.state.scheduler
    if alias not in scheduler._executors:
        return c.Paragraph(text=f"Executor({alias=}) not exists.")
    elif alias == "default":
        return c.Paragraph(text="Cannot remove default executor.")
    scheduler.remove_executor(alias)
    return c.Paragraph(text=f"Executor({alias=}) removed successfully.")


router = APIRouter(prefix="/job/executor", tags=["executor"])
router.add_api_route(
    path="",
    endpoint=store_exec,
    methods=["GET"],
    response_model=FastUI,
    response_model_exclude_none=True
)

router.add_api_route(
    path="/new",
    endpoint=new_executor,
    methods=["POST"],
    response_model=FastUI,
    response_model_exclude_none=True
)

router.add_api_route(
    path="/remove",
    endpoint=remove_executor,
    methods=["POST"],
    response_model=FastUI,
    response_model_exclude_none=True
)
