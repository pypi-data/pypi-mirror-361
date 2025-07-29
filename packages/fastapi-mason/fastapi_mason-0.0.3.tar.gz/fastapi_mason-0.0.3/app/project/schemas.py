from typing import TYPE_CHECKING

from tortoise.contrib.pydantic import PydanticModel, pydantic_model_creator

from app.project.meta import ProjectMeta
from app.project.models import Project

ProjectReadSchema = pydantic_model_creator(
    Project,
    meta_override=ProjectMeta,
    name='ProjectReadSchema',
)
ProjectCreateSchema = pydantic_model_creator(
    Project,
    meta_override=ProjectMeta,
    name='ProjectCreateSchema',
    exclude_readonly=True,
)

if TYPE_CHECKING:
    ProjectReadSchema = type('ProjectReadSchema', (Project, PydanticModel), {})
    ProjectCreateSchema = type('ProjectCreateSchema', (Project, PydanticModel), {})
