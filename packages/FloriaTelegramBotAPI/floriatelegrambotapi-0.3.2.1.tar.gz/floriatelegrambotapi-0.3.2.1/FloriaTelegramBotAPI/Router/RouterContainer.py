from typing import Any

from .. import Validator, Abc, Types


class RouterContainer(Abc.Container[Abc.Router]):
    def __init__(self, *routes: Abc.Router):
        self._routers: list[Abc.Router] = []
        self.Register(*routes)
    
    def Register(self, *routes: Abc.Router):
        self._routers += Validator.List(routes, Abc.Router)
    
    async def Invoke(self, obj: Types.UpdateObject, **kwargs: Any):
        for router in self._routers:
            if await router.Processing(obj, **kwargs):
                return True
        return False

    def __len__(self):
        return len(self._routers)
    