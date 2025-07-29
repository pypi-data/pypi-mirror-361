"""
Generic ViewSet class providing base functionality for FastAPI+ library.

This is the core class that contains all the base methods and setup logic.
Mixins will only add routes to this generic viewset.
"""

from typing import Any, Generic, List, Type

from fastapi import APIRouter, HTTPException
from tortoise.contrib.pydantic import PydanticModel
from tortoise.queryset import QuerySet

from fastapi_mason.pagination import DisabledPagination, Pagination
from fastapi_mason.permissions import BasePermission, check_permissions
from fastapi_mason.routes import register_action_route, sort_routes_by_specificity
from fastapi_mason.state import RequestState
from fastapi_mason.types import ModelType
from fastapi_mason.wrappers import PaginatedResponseWrapper, ResponseWrapper


class GenericViewSet(Generic[ModelType]):
    """
    Generic ViewSet providing base functionality for API endpoints.

    This class contains all the core logic for working with models, schemas,
    pagination, response formatting, permissions, and filtering.
    Mixins will add specific routes to this base class.
    """

    # Model and schema configuration
    model: Type[ModelType] = None
    create_schema: PydanticModel = None
    update_schema: PydanticModel = None
    read_schema: PydanticModel = None
    many_read_schema: PydanticModel = None

    # Pagination and response wrappers
    pagination: Pagination[ModelType] = DisabledPagination
    list_wrapper: ResponseWrapper[ModelType] | PaginatedResponseWrapper[ModelType, Pagination[ModelType]] | None = None
    single_wrapper: ResponseWrapper[ModelType] | None = None

    # Permission configuration
    permission_classes: List[Type[BasePermission]] = []

    # Router configuration
    router: APIRouter | None = None

    # State configuration
    state_class: type[RequestState] = RequestState

    # Internal state
    __routes_added: bool = False

    def __init__(self, *args, **kwargs):
        # Validate configuration before setup
        from .validation import validate_viewset_config

        validate_viewset_config(self.__class__)

        self.setup_schemas()
        super().__init__(*args, **kwargs)

        # Register custom actions
        self.register_actions()

        self.finalize_routes()

    @property
    def state(self) -> RequestState:
        """
        Get the current request state.

        Returns the RequestState object for the current request,
        which contains action name, request object, and custom data.

        Returns:
            Current RequestState or None if not in request context
        """
        return self.state_class.get_request_state()

    def setup_schemas(self):
        """
        Setup default schemas if not provided.

        This method ensures that all required schemas are available,
        using sensible defaults when specific schemas are not provided.
        """
        # Setup create/update schemas with fallbacks
        self.create_schema = self.create_schema or self.update_schema
        self.update_schema = self.update_schema or self.create_schema

        # Setup read schemas with fallbacks
        self.many_read_schema = self.many_read_schema or self.read_schema
        self.read_schema = self.read_schema or self.many_read_schema

        # Validate that we have all required schemas
        if not self.read_schema:
            raise ValueError(f"At least 'read_schema' must be provided for {self.__class__.__name__}")

        if not self.model:
            raise ValueError(f'Model must be provided for {self.__class__.__name__}')

    async def check_permissions(self, obj: Any = None) -> None:
        """
        Check permissions for the current request.

        Args:
            request: FastAPI request object
            obj: Object being accessed (for object-level permissions)

        Raises:
            HTTPException: 403 if permission is denied
        """
        await check_permissions(self.get_permissions(), self.state.request, self, obj)

    def get_permissions(self) -> List[BasePermission]:
        """
        Get permission instances for this viewset.

        Returns:
            List of permission instances
        """
        return [permission() for permission in self.permission_classes]

    def get_queryset(self) -> QuerySet[ModelType]:
        """
        Get base queryset for the model.

        Override this method to customize the base queryset
        (e.g., add filtering, prefetching, etc.).

        Returns:
            Base queryset for the model
        """
        return self.model.all()

    async def get_object(self, item_id: int) -> ModelType:
        """
        Get single object by ID with permission check.

        Override this method to customize object retrieval
        (e.g., add permission checks, custom lookup fields, etc.).

        Args:
            item_id: ID of the object to retrieve
            request: FastAPI request object for permission checks

        Returns:
            Model instance

        Raises:
            HTTPException: 404 if object not found, 403 if permission denied
        """
        queryset = self.get_queryset()
        obj = await queryset.get_or_none(id=item_id)
        if not obj:
            raise HTTPException(status_code=404, detail='Not found')

        # Check object-level permissions if request is provided
        await self.check_permissions(obj)

        return obj

    async def perform_create(self, obj: ModelType) -> ModelType:
        """
        Perform the actual object creation.

        Override this method to add custom logic during creation
        (e.g., setting additional fields, sending notifications, etc.).

        Args:
            obj: Object instance to save
            request: FastAPI request object

        Returns:
            Saved object instance
        """
        await obj.save()
        return obj

    async def perform_update(self, obj: ModelType) -> ModelType:
        """
        Perform the actual object update.

        Override this method to add custom logic during update
        (e.g., validation, logging, notifications, etc.).

        Args:
            obj: Object instance to save
            request: FastAPI request object

        Returns:
            Updated object instance
        """
        await obj.save()
        return obj

    async def perform_destroy(self, obj: ModelType) -> None:
        """
        Perform the actual object deletion.

        Override this method to add custom logic during deletion
        (e.g., soft delete, cleanup, notifications, etc.).

        Args:
            obj: Object instance to delete
            request: FastAPI request object
        """
        await obj.delete()

    def get_list_response_model(self) -> Any:
        """Get response model for list endpoint."""
        if self.list_wrapper:
            if issubclass(self.list_wrapper, ResponseWrapper):
                return self.list_wrapper[self.many_read_schema]
            elif issubclass(self.list_wrapper, PaginatedResponseWrapper):
                return self.list_wrapper[self.many_read_schema, self.pagination]
        return list[self.many_read_schema]

    def get_single_response_model(self) -> Any:
        """Get response model for single endpoint."""
        if self.single_wrapper:
            if issubclass(self.single_wrapper, ResponseWrapper):
                return self.single_wrapper[self.read_schema]
        return self.read_schema

    async def get_paginated_response(
        self,
        queryset: QuerySet[ModelType],
        pagination: Pagination[ModelType],
        wrapper: PaginatedResponseWrapper | None = None,
    ):
        """Get paginated response for queryset."""
        wrapper = wrapper or self.list_wrapper
        paginated_query = pagination.paginate(queryset)
        results = await self.many_read_schema.from_queryset(paginated_query)
        await pagination.fill_meta(queryset)

        if wrapper:
            return wrapper.wrap(data=results, pagination=pagination)

        return results

    def register_actions(self):
        """
        Register custom actions defined with @action decorator.

        This method scans the viewset class for methods marked with @action
        and automatically registers them as routes.
        """
        from .validation import validate_action_method

        # Get all methods from the class
        for method_name in dir(self.__class__):
            method = getattr(self.__class__, method_name)

            # Check if method is marked as action
            if hasattr(method, '_is_action') and method._is_action:
                # Validate action configuration
                validate_action_method(method, self.__class__)

                # Register the action as a route
                register_action_route(self, method)

    def finalize_routes(self):
        """
        Finalize routes after all mixins have added their routes.

        This method sorts routes by specificity and should be called
        after all mixins have registered their routes.
        """
        if not self.__routes_added:
            self.router.routes = sort_routes_by_specificity(self.router.routes)
            self.__routes_added = True
