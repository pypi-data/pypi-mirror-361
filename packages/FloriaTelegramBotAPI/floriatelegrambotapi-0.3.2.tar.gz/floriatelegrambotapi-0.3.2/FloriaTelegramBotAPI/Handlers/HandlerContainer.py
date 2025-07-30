from typing import Any, Type, Optional

from .. import Types
from .. import Validator
from .. import Abc, Protocols
from ..Middleware import Middleware


class HandlerContainer(Abc.Container[Abc.Handler]):
    def __init__(self, middleware: Optional[Abc.Middleware] = None):
        self._handlers: list[Abc.Handler] = []
        self._mixins: list[Type[Abc.Mixin]] = []
        self._middleware: Abc.Middleware = middleware or Middleware()
    
    def Register(
        self, 
        func: Protocols.Functions.HandlerCallableAsync[...], 
        handler: Abc.Handler, 
        *mixins: Type[Abc.Mixin], 
        **kwargs: Any
    ) -> Protocols.Functions.HandlerCallableAsync[...]:
        Validator.IsSubClass(handler.__class__, Abc.Handler)
        Validator.List(mixins, Abc.Mixin)
        
        if self._mixins or mixins:
            handler.__class__ = type(f'{handler.__class__.__name__}_Mixed', (*self._mixins, *mixins, handler.__class__), {}) # type: ignore
        
        handler.SetFunction(Validator.IsCallableAsync(func))
        for key, value in kwargs.items():
            handler.__setattr__(key, value)
        self._handlers.append(handler)
        
        return func
    
    async def Invoke(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        for handler in self._handlers:
            if await self._middleware.Invoke(handler, obj, **kwargs):
                return True
        return False
    
    @property
    def mixins(self) -> list[Type[Abc.Mixin]]:
        return self._mixins
    @mixins.setter
    def mixins(self, value: list[Type[Abc.Mixin]]):
        self._mixins = Validator.ListSubClassTypes(value, Abc.Mixin)
    
    @property
    def middleware(self) -> Abc.Middleware:
        return self._middleware
    @middleware.setter
    def middleware(self, value: Abc.Middleware):
        Validator.IsSubClass(value.__class__, Abc.Middleware)
        self._middleware = value
    
    def __len__(self):
        return len(self._handlers)