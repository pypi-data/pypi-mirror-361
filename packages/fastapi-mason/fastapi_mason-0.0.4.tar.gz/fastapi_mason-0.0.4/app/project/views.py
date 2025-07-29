from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.project.models import Project, Tast
from app.project.schemas import ProjectCreateSchema, ProjectReadSchema, TasksCreateSchema, TasksReadSchema
from fastapi_mason import decorators
from fastapi_mason.pagination import PageNumberPagination
from fastapi_mason.permissions import IsAuthenticatedOrReadOnly
from fastapi_mason.state import RequestState
from fastapi_mason.viewsets import ModelViewSet
from fastapi_mason.wrappers import PaginatedResponseDataWrapper, ResponseDataWrapper


class User(BaseModel):
    name: str = ''
    age: int = 0


async def validate_keks(request: Request):
    # _penis.set('????? THIS IS FROM DEPEND')
    # task = asyncio.current_task()
    RequestState.set_user({'THIS IS MY USER': True})
    # print(f'Coroutine ID (id of task): {id(task)}')

    # print(str(_penis.get()), 'from depend get')
    # request.state.user = '????'
    # RequestState.set_user(request.state.user)
    # print(RequestState.get_request_state().user)
    # print(get_request_state().user)


router = APIRouter(prefix='/projects', tags=['projects'], dependencies=[Depends(validate_keks)])


@decorators.viewset(router)
class ProjectViewSet(ModelViewSet[Project]):
    model = Project
    read_schema = ProjectReadSchema
    # many_read_schema = ProjectReadSchema
    create_schema = ProjectCreateSchema
    pagination = PageNumberPagination
    list_wrapper = PaginatedResponseDataWrapper
    single_wrapper = ResponseDataWrapper
    permission_classes = [IsAuthenticatedOrReadOnly]
    state_class = RequestState[User]

    @decorators.action(methods=['GET'])
    async def example(self):
        print(self)
        return 123

    @decorators.action(methods=['GET'])
    async def list(self):
        print(self.state.request)
        return self.state.request.query_params

    @decorators.action(methods=['POST'])
    async def create(self, request: Request, data: ProjectCreateSchema):
        return data


task_router = APIRouter(
    prefix='/tasks',
    tags=['tasks'],
)


@decorators.viewset(task_router)
class TaskViewSet(ModelViewSet[Project]):
    model = Tast
    read_schema = TasksReadSchema
    create_schema = TasksCreateSchema
    pagination = PageNumberPagination
    list_wrapper = PaginatedResponseDataWrapper
    single_wrapper = ResponseDataWrapper
