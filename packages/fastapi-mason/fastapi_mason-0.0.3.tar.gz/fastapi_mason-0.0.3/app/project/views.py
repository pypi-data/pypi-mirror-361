from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.project.models import Project
from app.project.schemas import ProjectCreateSchema, ProjectReadSchema
from fastapi_mason import decorators
from fastapi_mason.pagination import PageNumberPagination
from fastapi_mason.permissions import IsAuthenticatedOrReadOnly
from fastapi_mason.state import RequestState
from fastapi_mason.viewsets import ModelViewSet
from fastapi_mason.wrappers import PaginatedResponseDataWrapper, ResponseDataWrapper


class User(BaseModel):
    name: str = ''
    age: int = 0


async def setup_user(request: Request):
    # _penis.set('????? THIS IS FROM DEPEND')
    # task = asyncio.current_task()
    RequestState.set_user({'THIS IS MY USER': True})
    # print(f'Coroutine ID (id of task): {id(task)}')

    # print(str(_penis.get()), 'from depend get')
    # request.state.user = '????'
    # RequestState.set_user(request.state.user)
    # print(RequestState.get_request_state().user)
    # print(get_request_state().user)


router = APIRouter(prefix='/projects', tags=['projects'], dependencies=[Depends(setup_user)])


@decorators.viewset(router)
class ProjectViewSet(ModelViewSet[Project]):
    model = Project
    read_schema = ProjectReadSchema
    create_schema = ProjectCreateSchema
    pagination = PageNumberPagination
    list_wrapper = PaginatedResponseDataWrapper
    single_wrapper = ResponseDataWrapper
    permission_classes = [IsAuthenticatedOrReadOnly]
    state_class = RequestState[User]

    # def get_permissions(self) -> List[BasePermission]:
    #     print(self.state.action)
    #     if self.state.action in ['list']:
    #         return [DenyAll()]
    #     return []

    @decorators.action(methods=['GET'])
    async def my_action(self, request: Request):
        return {'message': 'my_action'}

    @decorators.action(methods=['GET'])
    async def list(self, request: Request):
        return {'message': 'my_action'}
