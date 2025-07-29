import logging
import re
from typing import Literal, Optional, List

from fastapi import APIRouter
from fastui import FastUI
from fastui import components as c
from fastui.components.forms import FormField, FormFieldSelect, FormFieldSelectSearch
from fastui.events import GoToEvent
from fastui.forms import SelectSearchResponse
from fastui.json_schema import SelectOption

from eagle_eye_scraper import CONFIG
from eagle_eye_scraper.scheduler_visual.shared import frame_page

PAGE_LINE = 1000

PARSE_PATTERN = re.compile(
    r"\[\s*(?P<pid>\d+)\] (?P<time>[\d\s:-]+) \| "
    # (?=\n\[|\Z): message match until next line start or end
    r"(?P<level>\w+)\s*\| (?P<name>.*?):(?P<line>\d+)\s(?P<message>.*?)(?=\n\[|\Z)",
    flags=re.S,  # match multiple lines
)

logger = logging.getLogger()


def parse_log_message(text: str):
    messages = text.strip().split("\n", 1)
    if len(messages) > 1:
        return f"{messages[0]}\n```\n{messages[1]}\n```"
    return messages[0]


def get_log_content(log_file: str, level: str):
    return [
        f"**[{line['pid']}] {line['time']}** *{line['level']}* "
        f"`{line['name']}:{line['line']}`: {parse_log_message(line['message'])}"
        for line in logger.parse(CONFIG.LOG_PATH / log_file, pattern=PARSE_PATTERN)
        if (not level or level == line["level"])
    ]


def get_local_job_logs(q: str = "") -> SelectSearchResponse:
    logs = [
        SelectOption(value=file.name, label=file.name)
        for file in sorted(CONFIG.LOG_PATH.iterdir(), reverse=True)
        if file.suffix == ".log" and file.name.startswith("jobs") and q in file.name
    ]
    return SelectSearchResponse(options=logs)


async def get_log(kind: Literal["jobs", "scheduler"],
                  log_file: Optional[str] = None,
                  level: str = "",
                  page: int = 1,
                  ):
    form_fields: List[FormField] = [
        FormFieldSelect(
            title="Level",
            name="level",
            placeholder="Filter by level",
            options=[
                {"value": level, "label": level}
                for level in logger._core.levels.keys()  # type: ignore
            ],
        )
    ]
    if kind == "jobs":
        if not log_file:
            field_initial = get_local_job_logs().options[0]
            if "options" in field_initial:
                field_initial = field_initial["options"][0]
            log_file = field_initial["value"]
        else:
            field_initial = SelectOption(value=log_file, label=log_file)

        form_fields.append(
            FormFieldSelectSearch(
                title="Log File",
                name="log_file",
                search_url="/api/available-logs",
                initial=field_initial,
            ),
        )
    else:
        log_file = "scheduler.log"

    if not (log_file and (CONFIG.LOG_PATH / log_file).exists()):
        return c.Error(title="File not found", description=f"Log file {log_file} not found.")

    contents = get_log_content(log_file, level)
    return frame_page(
        c.Heading(text="Logs"),
        c.LinkList(
            links=[
                c.Link(
                    components=[c.Text(text="Executor/Job/JobStore")],
                    on_click=GoToEvent(url="/log/jobs"),
                    active="/log/jobs",
                ),
                c.Link(
                    components=[c.Text(text="Scheduler")],
                    on_click=GoToEvent(url="/log/scheduler"),
                    active="/log/scheduler",
                ),
            ],
            mode="tabs",
            class_name="+ mb-4",
        ),
        c.Form(
            form_fields=form_fields,
            submit_url=".",
            method="GOTO",
            submit_on_change=True,
            display_mode="inline",
        ),
        c.Pagination(page=page, page_size=PAGE_LINE, total=len(contents) or 1),
        c.Markdown(
            text="\n\n".join(contents[(page - 1) * PAGE_LINE: page * PAGE_LINE]),
            class_name="border rounded p-2 mb-2",
        ),
        c.Pagination(page=page, page_size=PAGE_LINE, total=len(contents) or 1),
    )


router = APIRouter(prefix="/job/log", tags=["job_log"])

router.add_api_route(
    path="/{kind}",
    endpoint=get_log,
    methods=["GET"],
    response_model=FastUI,
    response_model_exclude_none=True
)
