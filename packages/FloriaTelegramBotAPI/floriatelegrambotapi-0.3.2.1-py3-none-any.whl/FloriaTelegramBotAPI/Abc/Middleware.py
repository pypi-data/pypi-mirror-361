from typing import Any
from abc import ABC, abstractmethod

from .. import Types
from .Handler import Handler
from .Filter import Filter


class Middleware(ABC):
    @abstractmethod
    def __init__(self, *filters: Filter):
        ...
    
    @abstractmethod
    async def Invoke(self, handler: Handler, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        ...