# FastAPI Mason Library Documentation

## Overview
FastAPI Mason is a Django REST Framework-inspired library that provides ViewSets and utilities for FastAPI applications with Tortoise ORM integration. It offers familiar DRF patterns like ViewSets, permissions, filtering, pagination, and custom actions.

## Core Components

### ViewSets
- **ModelViewSet**: Full CRUD operations (List, Create, Retrieve, Update, Delete)
- **ReadOnlyViewSet**: Read-only operations (List, Retrieve)
- **GenericViewSet**: Base class for custom viewsets

### Key Features
- Automatic route registration with `@viewset` decorator
- Custom actions with `@action` decorator
- Permission system (AllowAny, IsAuthenticated, IsOwner, etc.)
- Filtering backends (Search, Ordering, Django-style, Range)
- Pagination (LimitOffset, PageNumber, Cursor)
- Response wrappers for consistent API formatting
- **Universal decorator system** - all endpoints go through the same decorator pipeline

## Universal Decorator System

All endpoints (both from mixins and @action methods) now go through a **unified** decorator system via `create_endpoint_wrapper`. This ensures consistent behavior across all endpoints without any if/else logic.

### Key Principles:
- **One function for all**: No distinction between @action and mixin methods
- **Clean and simple**: Just prints current time when method is called
- **Easy to extend**: Add your logic in one place, applies to all endpoints
- **Preserves metadata**: Function signatures, names, and docs are maintained

### How It Works

```python
# In fastapi_mason/routes.py
def create_endpoint_wrapper(
    viewset: 'GenericViewSet',
    original_func: Callable,
    action_name: str,
) -> Callable:
    """
    Universal wrapper that applies to ALL endpoints.
    
    Simple, clean, and unified approach.
    """
    async def wrapped_endpoint(*args, **kwargs):
        # Print current time
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[{current_time}] {action_name} called")
        
        # Call original function
        return await original_func(*args, **kwargs)
    
    # Preserve function metadata
    wrapped_endpoint.__signature__ = original_sig
    wrapped_endpoint.__name__ = original_func.__name__
    wrapped_endpoint.__doc__ = original_func.__doc__
    
    return wrapped_endpoint
```

### All Endpoints Are Equal

```python
@viewset(router)
class UserViewSet(ModelViewSet[User]):
    model = User
    read_schema = UserRead
    
    # This @action method uses create_endpoint_wrapper
    @action(methods=['POST'], detail=True)
    async def set_password(self, item_id: int, password: str):
        return {"message": "Password updated"}
    
    # These mixin methods ALSO use create_endpoint_wrapper:
    # - list (GET /) 
    # - create (POST /)
    # - retrieve (GET /{item_id})
    # - update (PUT/PATCH /{item_id})
    # - destroy (DELETE /{item_id})
    
    # ALL methods print time when called!
```

### Example Output

```
[14:25:32] list called
[14:25:45] create called
[14:26:01] my_action called
[14:26:15] update called
```

### Extending the System

To add custom functionality to **ALL** endpoints, simply modify the `wrapped_endpoint` function:

```python
async def wrapped_endpoint(*args, **kwargs):
    # Your custom logic here
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] {action_name} called")
    
    # Add any custom logic:
    # - Authentication
    # - Rate limiting
    # - Caching
    # - Logging
    # - Monitoring
    # - etc.
    
    # Call original function
    return await original_func(*args, **kwargs)
```

### Benefits

1. **Unified approach**: No if/else logic between different method types
2. **Clean code**: Simple and readable implementation
3. **Easy maintenance**: One place to add logic for all endpoints
4. **Consistent behavior**: All endpoints work exactly the same way
5. **Extensible**: Easy to add new functionality

## Basic Usage

```python
from fastapi import APIRouter
from fastapi_mason import ModelViewSet, viewset
from tortoise.contrib.pydantic import pydantic_model_creator
from myapp.models import User

# Create schemas
UserRead = pydantic_model_creator(User)
UserCreate = pydantic_model_creator(User, exclude_readonly=True)

router = APIRouter(prefix="/users")

@viewset(router)
class UserViewSet(ModelViewSet[User]):
    model = User
    read_schema = UserRead
    create_schema = UserCreate
    
    # Optional configurations
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'email']
    pagination = PageNumberPagination
```

## Custom Actions

```python
@viewset(router)
class UserViewSet(ModelViewSet[User]):
    model = User
    read_schema = UserRead
    
    @action(methods=['POST'], detail=True)
    async def set_password(self, item_id: int, password: str):
        user = await self.get_object(item_id)
        # Custom logic here
        return {"message": "Password updated"}
    
    @action(methods=['GET'], detail=False, path='active')
    async def active_users(self):
        return await User.filter(is_active=True)
```

## Configuration Options

### Schemas
- `read_schema`: For retrieving objects
- `create_schema`: For creating objects  
- `update_schema`: For updating objects
- `many_read_schema`: For list responses

### Permissions
- `AllowAny`: No restrictions
- `IsAuthenticated`: Requires authentication
- `IsOwner`: Object-level ownership
- `IsAdminUser`: Admin/staff only

### Filtering
- `SearchFilter`: Text search across fields
- `OrderingFilter`: Field-based ordering
- `DjangoFilterBackend`: Django-style filtering
- `RangeFilter`: Range filtering for numeric/date fields

### Pagination
- `DisabledPagination`: No pagination
- `LimitOffsetPagination`: Offset/limit style
- `PageNumberPagination`: Page/size style
- `CursorPagination`: Cursor-based

### Response Wrappers
- `ResponseDataWrapper`: Simple data wrapping
- `StatusResponseWrapper`: Include status field
- `PaginatedResponseDataWrapper`: Paginated responses

## Architecture

1. **GenericViewSet**: Core functionality (filtering, permissions, object retrieval)
2. **Mixins**: Add specific routes (ListMixin, CreateMixin, etc.)
3. **Decorators**: `@viewset` for registration, `@action` for custom endpoints
4. **Universal Decorator System**: All endpoints go through `create_endpoint_wrapper`
5. **Validation**: Configuration validation and error handling
6. **Routes**: Automatic route registration and sorting

## Key Methods to Override

```python
class CustomViewSet(ModelViewSet[MyModel]):
    def get_queryset(self):
        """Customize base queryset"""
        return super().get_queryset().filter(user=self.request.user)
    
    async def perform_create(self, obj, request=None):
        """Custom creation logic"""
        obj.user = request.user  # Example: set owner
        return await super().perform_create(obj, request)
    
    async def get_object(self, item_id, request=None):
        """Custom object retrieval"""
        return await super().get_object(item_id, request)
```

This library provides a familiar DRF-like experience for FastAPI developers while leveraging FastAPI's performance and modern Python features.