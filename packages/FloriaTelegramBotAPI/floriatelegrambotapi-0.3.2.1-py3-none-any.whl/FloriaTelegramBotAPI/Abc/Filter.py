from typing import Any, Literal
from abc import ABC, abstractmethod

from .. import Types


class Filter(ABC):
    @abstractmethod
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        ...
