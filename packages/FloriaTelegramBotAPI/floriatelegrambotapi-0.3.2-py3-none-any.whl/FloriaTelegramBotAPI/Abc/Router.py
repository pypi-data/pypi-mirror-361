from typing import Any, Type
from abc import ABC, abstractmethod

from .. import Types
from .Handler import Handler
from .. import Protocols


class Router(ABC):
    @abstractmethod
    async def Processing(self, obj: Types.UpdateObject, **kwargs: Any) -> bool: ...
    
    @abstractmethod
    def Mount(self, router: 'Router'): ...
    
    @abstractmethod
    def AddHandler(self, handler: Handler) -> Protocols.Functions.WrapperHandlerCallable: ...
    
    @abstractmethod
    def Exception(self, exception: Type[Exception]) -> Protocols.Functions.WrapperExceptionCallable: ...
    
    @abstractmethod 
    def __len__(self) -> int: ...
