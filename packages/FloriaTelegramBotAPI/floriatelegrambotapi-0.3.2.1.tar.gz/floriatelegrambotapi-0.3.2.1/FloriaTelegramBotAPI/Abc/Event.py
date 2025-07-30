from typing import Generic
from abc import ABC, abstractmethod

from ..Protocols.Functions import TCommonCallableAny


class Event(ABC, Generic[TCommonCallableAny]):
    @abstractmethod
    def Register(self, func: TCommonCallableAny):
        ...
    
    @abstractmethod
    async def Invoke(self):
        ...
    
    async def __call__(self):
        return await self.Invoke()