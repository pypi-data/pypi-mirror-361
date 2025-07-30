from typing import Any

from ..Filters.FilterContainer import FilterContainer
from .. import Abc, Types


class Middleware(Abc.Middleware):
    def __init__(self, *filters: Abc.Filter):
        self._filters = FilterContainer(*filters)
    
    async def Invoke(self, handler: Abc.Handler, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        if await self._filters.Invoke(obj, **kwargs):
            return await handler.Invoke(obj, **kwargs)
        return False
