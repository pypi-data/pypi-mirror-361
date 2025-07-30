from typing import Any, Generic
import inspect

from .. import Abc
from ..Protocols.Functions import TCommonCallableAny


class Event(Abc.Event[TCommonCallableAny], Generic[TCommonCallableAny]):
    def __init__(self):
        self._funcs: list[tuple[TCommonCallableAny, tuple[Any], dict[str, Any]]] = []
    
    def Register(self, func: TCommonCallableAny, *args: Any, **kwargs: Any):
        self._funcs.append((func, args, kwargs))
    
    async def Invoke(self):
        for func, args, kwargs in self._funcs:
            if inspect.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
