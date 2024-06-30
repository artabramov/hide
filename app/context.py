from contextvars import ContextVar
from functools import lru_cache
from typing import Any

local_context_vars: ContextVar[dict] = ContextVar("local_context_vars",
                                                  default={})


class Context:
    """
    The class is used to work with context variables in cases when the app
    is not available (thread-local concept that works with asyncio tasks also):
    https://docs.python.org/3/library/contextvars.html
    """

    def __setattr__(self, key: str, value: Any) -> None:
        """Set a value for the context variable."""
        vars = local_context_vars.get()
        vars[key] = value
        local_context_vars.set(vars)

    def __getattr__(self, key: str) -> Any:
        """Get a value of the context variable."""
        vars = local_context_vars.get()
        return vars.get(key)


def get_context():
    return Context()
