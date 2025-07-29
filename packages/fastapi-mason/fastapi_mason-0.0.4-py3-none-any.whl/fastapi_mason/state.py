from contextvars import ContextVar
from typing import Any, Generic, Optional

from fastapi import Request

from fastapi_mason.types import T


class RequestState(Generic[T]):
    """
    State object that stores request-specific data.
    Available throughout the request lifecycle via self.state in viewsets.
    """

    def __init__(self, action: str = '', request: Request = None, *args, **kwargs):
        self.action = action
        self.request = request
        self.user: T | None = None

        self._data: dict[str, Any] = {}  # Custom data

    @staticmethod
    def set_user(user: T) -> None:
        """Set the current request state."""
        RequestState.get_request_state().user = user

    @classmethod
    def get_request_state(cls, *args, **kwargs) -> 'RequestState':
        """Get the current request state."""
        _current_state = _request_state_var.get()
        if _current_state is None:
            _current_state = cls(*args, **kwargs)
            _request_state_var.set(_current_state)
        return _current_state

    def set(self, key: str, value: Any) -> None:
        """Set a value in the state."""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        """Check if key exists in state."""
        return key in self._data

    def remove(self, key: str) -> None:
        """Remove a key from state."""
        self._data.pop(key, None)

    def clear(self) -> None:
        """Clear all custom data (keeps action and request)."""
        self._data.clear()

    def __repr__(self) -> str:
        return f'<RequestState state={self.__dict__}>'


# Context variable to store the current request state
_request_state_var: ContextVar[Optional[RequestState]] = ContextVar('_mason_request_state', default=None)


def clear_request_state() -> None:
    """Clear the current request state."""
    _request_state_var.set(None)
