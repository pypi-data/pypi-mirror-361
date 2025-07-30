from typing import Any

from .. import Types
from .. import Abc, Validator


class FilterContainer(Abc.Container[Abc.Filter]):
    def __init__(self, *filters: Abc.Filter):
        self._filters: list[Abc.Filter] = []
        
        self.Register(*filters)
    
    def Register(self, *filters: Abc.Filter):    
        self._filters += Validator.List(filters, Abc.Filter)
    
    async def Invoke(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        for filter in self._filters:
            if not await filter.Check(obj, **kwargs):
                return False
        return True
    
    def __len__(self) -> int:
        return len(self._filters)