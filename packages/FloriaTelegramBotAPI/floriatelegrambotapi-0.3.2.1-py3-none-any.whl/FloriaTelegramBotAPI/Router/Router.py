from typing import Any, Type

from .. import Types
from ..Handlers import HandlerContainer, Handler
from ..Filters.FilterContainer import FilterContainer
from ..Exceptions import ExceptionContainer
from .. import Protocols, Abc
from .RouterContainer import RouterContainer


class Router(Abc.Router):
    def __init__(self, *filters: Abc.Filter):
        self._filters: FilterContainer = FilterContainer(*filters)
        self._handlers: HandlerContainer = HandlerContainer()
        self._routers: RouterContainer = RouterContainer()
        self._exceptions: ExceptionContainer = ExceptionContainer()
    
    async def Processing(self, obj: Types.UpdateObject, **kwargs: Any):
        try:
            if await self._filters.Invoke(obj, **kwargs) and \
                (
                    await self._handlers.Invoke(obj, **kwargs) or 
                    await self._routers.Invoke(obj, **kwargs)
                ):
                    return True
                
            return False
        
        except Exception as ex:
            if not await self._exceptions.Invoke(ex, obj=obj, **kwargs):
                raise
            
            return False
    
    def Mount(self, router: Abc.Router):
        self._routers.Register(router)
    
    def AddHandler(self, handler: Abc.Handler):
        def wrapper(func: Protocols.Functions.HandlerCallableAsync[...]):
            return self._handlers.Register(func, handler)
        return wrapper
    
    def Exception(self, exception: Type[Exception]):
        def wrapper(func: Protocols.Functions.ExceptionCallableAsync):
            return self._exceptions.Register(exception, func)
        return wrapper
    
    def __len__(self) -> int:
        return len(self._routers)
    
    
    @property
    def middleware(self) -> Abc.Middleware:
        return self._handlers.middleware
    @middleware.setter
    def middleware(self, value: Abc.Middleware):
        self._handlers.middleware = value
        
    def Callback(
        self,
        *filters: Abc.Filter,
        **kwargs: Any
    ) -> Protocols.Functions.WrapperHandlerCallable:
        def wrapper(func: Protocols.Functions.HandlerCallableAsync[...]) -> Protocols.Functions.HandlerCallableAsync[...]:
            from ..Handlers.Handlers import CallbackHandler
            return self._handlers.Register(func, CallbackHandler(*filters, **kwargs))
        return wrapper
    
    def Message(
        self,
        *filters: Abc.Filter,
        **kwargs: Any
    ) -> Protocols.Functions.WrapperHandlerCallable:
        def wrapper(func: Protocols.Functions.HandlerCallableAsync[...]) -> Protocols.Functions.HandlerCallableAsync[...]:
            from ..Handlers.Handlers import MessageHandler
            return self._handlers.Register(func, MessageHandler(*filters, **kwargs))
        return wrapper
    
    def Handler(
        self,
        *filters: Abc.Filter,
        **kwargs: Any
    ) -> Protocols.Functions.WrapperHandlerCallable:
        def wrapper(func: Protocols.Functions.HandlerCallableAsync[...]) -> Protocols.Functions.HandlerCallableAsync[...]:
            return self._handlers.Register(func, Handler(*filters, **kwargs))
        return wrapper
