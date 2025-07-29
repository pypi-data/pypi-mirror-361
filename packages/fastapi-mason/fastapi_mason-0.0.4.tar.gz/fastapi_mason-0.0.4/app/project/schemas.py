from typing import TYPE_CHECKING

from tortoise.contrib.pydantic import PydanticModel

from app.project.meta import get_project_with_tasks_meta, get_task_with_project_meta
from app.project.models import Project, Tast
from fastapi_mason.schemas import generate_schema, rebuild_schema

ProjectReadSchema = generate_schema(Project, name='ProjectReadSchema', meta=get_project_with_tasks_meta())
ProjectCreateSchema = rebuild_schema(ProjectReadSchema, name='ProjectCreateSchema', exclude_readonly=True)


TasksReadSchema = generate_schema(Tast, name='TasksReadSchema', meta=get_task_with_project_meta())
TasksCreateSchema = rebuild_schema(TasksReadSchema, name='TasksCreateSchema', exclude_readonly=True)


if TYPE_CHECKING:
    ProjectReadSchema = type('ProjectCreateSchema', (Project, PydanticModel), {})
    ProjectCreateSchema = type('ProjectCreateSchema', (Project, PydanticModel), {})

    TaskReadSchema = type('TaskReadSchema', (Tast, PydanticModel), {})
    TaskCreateSchema = type('TaskCreateSchema', (Tast, PydanticModel), {})
