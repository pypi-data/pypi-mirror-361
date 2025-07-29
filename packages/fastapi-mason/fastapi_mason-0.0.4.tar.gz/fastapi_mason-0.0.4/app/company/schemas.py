from tortoise.contrib.pydantic import pydantic_model_creator

from app.company.models import Company

CompanyLightSchema = pydantic_model_creator(
    Company,
    include=('id', 'name'),
    name='CompanyLightSchema',
    # project
)
