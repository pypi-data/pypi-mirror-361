from fastapi import APIRouter, FastAPI

from app.core.database import register_database
from app.project.views import router as project_router
from app.project.views import task_router

app = FastAPI(
    title='My FastAPI Project',
    version='1.0.0',
    description='REST API with FastAPI, Tortoise ORM and Aerich',
)
register_database(app)

router = APIRouter(prefix='/api')


app.include_router(project_router)
app.include_router(task_router)
