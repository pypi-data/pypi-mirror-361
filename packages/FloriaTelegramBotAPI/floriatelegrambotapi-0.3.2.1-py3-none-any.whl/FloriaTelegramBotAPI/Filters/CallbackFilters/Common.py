from typing import Callable, Any, Literal, cast
import json

from ... import Abc, Types


class IsCallback(Abc.Filter):
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        return isinstance(obj, Types.CallbackQuery)


class IsDeserialize(IsCallback):
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        if not await super().Check(obj, **kwargs):
            return False
        
        query = cast(Types.CallbackQuery, obj)
        
        if query.data is None:
            return False
        
        try:
            return json.loads(query.data)
        
        except json.JSONDecodeError:
            return False


class Fields(IsDeserialize):
    def __init__(self, **values: Any | Callable[[Any], bool]):
        self._values = values
    
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        data = await super().Check(obj, **kwargs)
        if data is False:
            return False
        
        if not isinstance(data, dict):
            raise RuntimeError()
        
        for key, value in self._values.items():
            if key not in data or (
                not value(data[key])
                if isinstance(value, Callable) else 
                data[key] != value 
            ):
                return False
        
        return True
                