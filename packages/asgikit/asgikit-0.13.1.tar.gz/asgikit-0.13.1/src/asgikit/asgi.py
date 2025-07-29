from collections.abc import Awaitable, Callable
from typing import Any, TypeAlias

__all__ = (
    "AsgiScope",
    "AsgiReceive",
    "AsgiSend",
    "AsgiException",
)


AsgiScope: TypeAlias = dict[str, Any]
AsgiReceive: TypeAlias = Callable[..., Awaitable[dict]]
AsgiSend: TypeAlias = Callable[[dict], Awaitable]


class AsgiException(Exception):
    pass
