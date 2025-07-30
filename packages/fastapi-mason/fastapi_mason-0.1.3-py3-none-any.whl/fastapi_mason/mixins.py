"""
Mixins for FastAPI Mason viewsets.

These mixins only add specific routes to the GenericViewSet.
They do not contain any business logic - all logic is in GenericViewSet.
"""

from typing import TYPE_CHECKING, Generic

from fastapi import Depends
from pydantic import BaseModel

from fastapi_mason.pagination import DisabledPagination
from fastapi_mason.routes import BASE_ROUTE_PATHS, add_wrapped_route
from fastapi_mason.types import ModelType

if TYPE_CHECKING:
    from fastapi_mason.generics import GenericViewSet


class ListMixin(Generic[ModelType]):
    """Mixin that adds list endpoint to GenericViewSet."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_list_route()  # type: ignore

    def add_list_route(self: 'GenericViewSet'):  # type: ignore
        async def list_endpoint(
            pagination=Depends(self.pagination.from_query),
        ):
            queryset = self.get_queryset()

            if not isinstance(pagination, DisabledPagination):
                return await self.get_paginated_response(queryset=queryset, pagination=pagination)

            results = await self.many_read_schema.from_queryset(queryset)  # type: ignore

            if self.list_wrapper:
                return self.list_wrapper.wrap(data=results, pagination=pagination)

            return results

        add_wrapped_route(
            viewset=self,
            name='list',
            path=BASE_ROUTE_PATHS['list'],
            endpoint=list_endpoint,
            methods=['GET'],
            response_model=self.get_list_response_model(),
        )


class RetrieveMixin(Generic[ModelType]):
    """Mixin that adds retrieve endpoint to GenericViewSet."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_retrieve_route()  # type: ignore

    def add_retrieve_route(self: 'GenericViewSet'):  # type: ignore
        async def retrieve_endpoint(item_id: int):
            obj = await self.get_object(item_id)
            result = await self.read_schema.from_tortoise_orm(obj)  # type: ignore

            if self.single_wrapper:
                return self.single_wrapper.wrap(data=result)

            return result

        add_wrapped_route(
            viewset=self,
            name='retrieve',
            path=BASE_ROUTE_PATHS['retrieve'],
            endpoint=retrieve_endpoint,
            methods=['GET'],
            response_model=self.get_single_response_model(),
        )


class CreateMixin(Generic[ModelType]):
    """Mixin that adds create endpoint to GenericViewSet."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_create_route()  # type: ignore

    def add_create_route(self: 'GenericViewSet'):  # type: ignore
        async def create_endpoint(data: self.create_schema):  # type: ignore
            data = await self.validate_data(data)
            if isinstance(data, BaseModel):
                data = data.model_dump(exclude_unset=True)

            obj = self.model(**data)
            await self.before_save(obj)
            obj = await self.perform_create(obj)  # type: ignore
            await self.after_save(obj)
            result = await self.read_schema.from_tortoise_orm(obj)  # type: ignore

            if self.single_wrapper:
                return self.single_wrapper.wrap(data=result)

            return result

        add_wrapped_route(
            viewset=self,
            name='create',
            path=BASE_ROUTE_PATHS['create'],
            endpoint=create_endpoint,
            methods=['POST'],
            response_model=self.get_single_response_model(),
            status_code=201,
        )

    async def perform_create(self, obj: ModelType) -> ModelType:
        """Perform the actual object creation."""
        await obj.save()
        return obj


class UpdateMixin(Generic[ModelType]):
    """Mixin that adds update endpoint to GenericViewSet."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_update_route()  # type: ignore

    def add_update_route(self: 'GenericViewSet'):  # type: ignore
        async def update_endpoint(item_id: int, data: self.update_schema):  # type: ignore
            obj = await self.get_object(item_id)

            data = await self.validate_data(data)
            if isinstance(data, BaseModel):
                data = data.model_dump(exclude_unset=True)

            for key, value in data.items():
                setattr(obj, key, value)

            await self.before_save(obj)
            obj = await self.perform_update(obj)  # type: ignore
            await self.after_save(obj)
            result = await self.read_schema.from_tortoise_orm(obj)  # type: ignore

            if self.single_wrapper:
                return self.single_wrapper.wrap(data=result)

            return result

        add_wrapped_route(
            viewset=self,
            name='update',
            path=BASE_ROUTE_PATHS['update'],
            endpoint=update_endpoint,
            methods=['PUT', 'PATCH'],
            response_model=self.get_single_response_model(),
        )

    async def perform_update(self, obj: ModelType) -> ModelType:
        """Perform the actual object update."""
        await obj.save()
        return obj


class DestroyMixin(Generic[ModelType]):
    """Mixin that adds destroy endpoint to GenericViewSet."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_destroy_route()  # type: ignore

    def add_destroy_route(self: 'GenericViewSet'):  # type: ignore
        async def destroy_endpoint(item_id: int):
            obj = await self.get_object(item_id)
            await self.perform_destroy(obj)  # type: ignore

        add_wrapped_route(
            viewset=self,
            name='destroy',
            path=BASE_ROUTE_PATHS['destroy'],
            endpoint=destroy_endpoint,
            methods=['DELETE'],
            status_code=204,
        )

    async def perform_destroy(self, obj: ModelType) -> None:
        """Perform the actual object deletion."""
        await obj.delete()
