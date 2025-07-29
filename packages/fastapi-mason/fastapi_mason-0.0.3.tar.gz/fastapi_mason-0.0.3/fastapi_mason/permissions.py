"""
Permission system for FastAPI+ viewsets.

Provides permission classes and utilities for access control,
similar to Django REST Framework permissions.
"""

from typing import TYPE_CHECKING, Any, List

from fastapi import HTTPException, Request

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

if TYPE_CHECKING:
    from fastapi_mason.generics import GenericViewSet


class BasePermission:
    """
    Base class for all permission classes.

    Permission classes are used to grant or deny access to viewset actions.
    They can check user authentication, authorization, object ownership, etc.
    """

    PERMISSION_DENIED_MESSAGE = 'Permission denied'
    OBJECT_PERMISSION_DENIED_MESSAGE = 'Object permission denied'

    async def has_permission(self, request: Request, view: 'GenericViewSet') -> bool:
        """
        Return `True` if permission is granted, `False` otherwise.

        This method is called for all actions to check general permissions.

        Args:
            request: The FastAPI request object
            view: The viewset instance

        Returns:
            True if permission granted, False otherwise
        """
        return True

    async def has_object_permission(self, request: Request, view: 'GenericViewSet', obj: Any) -> bool:
        """
        Return `True` if permission is granted for the specific object, `False` otherwise.

        This method is called for object-level actions (retrieve, update, delete).

        Args:
            request: The FastAPI request object
            view: The viewset instance
            obj: The object being accessed

        Returns:
            True if permission granted, False otherwise
        """
        return True


class DenyAll(BasePermission):
    """
    Deny all permissions.
    """

    async def has_permission(self, request: Request, view: 'GenericViewSet') -> bool:
        return False

    async def has_object_permission(self, request: Request, view: 'GenericViewSet', obj: Any) -> bool:
        return False


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.

    Requires that request.state.user exists and is not None.
    You need to set up authentication middleware to populate request.state.user.
    """

    async def has_permission(self, request: Request, view: 'GenericViewSet') -> bool:
        return bool(view.state.user)


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Allows read-only access to any user, and full access to authenticated users.
    """

    async def has_permission(self, request: Request, view: 'GenericViewSet') -> bool:
        """Allow read access to all, write access to authenticated users."""
        return request.method in SAFE_METHODS or bool(view.state.user)


# Permission utilities


async def check_permissions(
    permission_classes: List[BasePermission], request: Request, view: 'GenericViewSet', obj: Any | None = None
) -> None:
    """
    Check all permissions and raise HTTP 403 if any permission is denied.

    Args:
        permission_classes: List of permission classes to check
        request: FastAPI request object
        view: Viewset instance
        obj: Object being accessed (for object-level permissions)

    Raises:
        HTTPException: 403 Forbidden if any permission is denied
    """
    for permission in permission_classes:
        # Check general permissions
        if not await permission.has_permission(request, view):
            raise HTTPException(status_code=403, detail=permission.PERMISSION_DENIED_MESSAGE)

        # Check object-level permissions if object is provided
        if obj is not None:
            if not await permission.has_object_permission(request, view, obj):
                raise HTTPException(status_code=403, detail=permission.OBJECT_PERMISSION_DENIED_MESSAGE)
