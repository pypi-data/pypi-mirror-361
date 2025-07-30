from typing import Any
from abc import ABC, abstractmethod

from .. import Types
from .. import Protocols


class Handler(ABC):
    @abstractmethod
    async def Validate(self, obj: Types.UpdateObject, **kwargs: Any) -> bool: ...

    @abstractmethod
    def GetPassedByType(self, obj: Types.UpdateObject, **kwargs: Any) -> list[Any]: ...
    
    @abstractmethod
    def GetPassedByName(self, obj: Types.UpdateObject, **kwargs: Any) -> dict[str, Any]: ...

    @abstractmethod
    async def Invoke(self, obj: Types.UpdateObject, **kwargs: Any) -> bool: ...
    
    @abstractmethod
    async def PostInvoke(self, result: bool, obj: Types.UpdateObject, **kwargs: Any) -> bool: ...
    
    @abstractmethod
    def SetFunction(self, func: Protocols.Functions.HandlerCallableAsync[...]): ...