from typing import Any

from .FilterContainer import FilterContainer
from .. import Extractor, Enums, Validator, Abc, Types


class Not(Abc.Filter):
    def __init__(self, filter: Abc.Filter):
        Validator.IsSubClass(filter.__class__, Abc.Filter)
        
        self._filter: Abc.Filter = filter
    
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        return not await self._filter.Check(obj, **kwargs)


class Or(Abc.Filter):
    def __init__(self, *filters: Abc.Filter):
        self._filters = FilterContainer(*filters)
    
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        return await self._filters.Invoke(obj, **kwargs)


class Chat(Abc.Filter):
    def __init__(self, *types: Enums.ChatType):
        self._types: list[Enums.ChatType] = Validator.List(types, Enums.ChatType, subclass=False)
    
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        return Extractor.GetChat(obj).type in self._types

