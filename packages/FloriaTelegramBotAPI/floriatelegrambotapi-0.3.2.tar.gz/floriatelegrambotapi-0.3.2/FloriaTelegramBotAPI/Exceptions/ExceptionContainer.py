from typing import Any, Type

from .. import Validator, Abc, Protocols


class ExceptionContainer(Abc.Container[Exception]):
    def __init__(self):
        self._exceptions: list[tuple[Type[Exception], Protocols.Functions.ExceptionCallableAsync]] = []
    
    def Register(self, exception: Type[Exception], func: Protocols.Functions.ExceptionCallableAsync) -> Protocols.Functions.ExceptionCallableAsync:
        Validator.IsSubClass(exception, Exception)
        self._exceptions.append(
            (
                exception, 
                Validator.IsCallableAsync(func)
            )
        )
        return func
        
    async def Invoke(self, exception: Exception, **kwargs: Any) -> bool:
        kwargs['bot'].logger.error(exception.__class__.__name__, exc_info=True) 
        
        for ex, func in self._exceptions:
            if not issubclass(exception.__class__, ex):
                continue
            
            if await func(exception, **kwargs) is not False:
                return True
            
        return False

    def __len__(self):
        return len(self._exceptions)