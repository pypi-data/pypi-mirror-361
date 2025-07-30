from typing import Any, Optional

from ..Filters.FilterContainer import FilterContainer
from .. import Extractor, Utils, Abc, Protocols, Types


class Handler(Abc.Handler):
    def __init__(
        self,
        *filters: Abc.Filter,
        **kwargs: dict[str, Any]
    ):
        self._func: Optional[Protocols.Functions.HandlerCallableAsync[...]] = None
        self._filters = FilterContainer(*filters)
        self._kwargs = kwargs
    
    async def Validate(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        return await self._filters.Invoke(obj, **kwargs)

    def GetPassedByType(self, obj: Types.UpdateObject, **kwargs: Any) -> list[Any]:
        return [
            obj,
            kwargs.get('bot'),
            Utils.LazyObject(Types.User, lambda: Extractor.GetUser(obj)),
            Utils.LazyObject(Types.Chat, lambda: Extractor.GetChat(obj))
        ]
    
    def GetPassedByName(self, obj: Types.UpdateObject, **kwargs: Any) -> dict[str, Any]:
        return {}

    async def Invoke(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        if self._func is None:
            raise RuntimeError()
        
        if await self.Validate(obj, **kwargs):
            return await self.PostInvoke(
                await Utils.InvokeFunction(
                    self._func,
                    passed_by_name=self.GetPassedByName(obj, **kwargs),
                    passed_by_type=self.GetPassedByType(obj, **kwargs)
                ),
                obj,
                **kwargs
            ) is not False
        return False
    
    async def PostInvoke(self, result: bool, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        return result
    
    def SetFunction(self, func: Protocols.Functions.HandlerCallableAsync[...]):
        self._func = func