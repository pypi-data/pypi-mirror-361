from typing import Any, Protocol, TypeVar, Literal, Union, ParamSpec


P = ParamSpec("P")


class CommonCallable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...
TCommonCallable = TypeVar("TCommonCallable", bound=CommonCallable)

class WrappedCommonCallable(Protocol):
    def __call__(self, func: CommonCallable) -> CommonCallable:
        ...
TWrappedCommonCallable = TypeVar("TWrappedCommonCallable", bound=WrappedCommonCallable)

class CommonCallableAsync(Protocol):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...
TCommonCallableAsync = TypeVar("TCommonCallableAsync", bound=CommonCallableAsync)

class KwargsCallableAsync(Protocol):
    async def __call__(self, **kwargs: Any) -> Any:
        ...
TKwargsCallableAsync = TypeVar("TKwargsCallableAsync", bound=KwargsCallableAsync)

class HandlerCallableAsync(Protocol[P]):
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Union[Any, Literal[False]]:
        ...
THandlerCallableAsync = TypeVar("THandlerCallableAsync", bound=HandlerCallableAsync[...])

class WrapperHandlerCallable(Protocol):
    def __call__(self, func: HandlerCallableAsync[...]) -> HandlerCallableAsync[...]:
        ...
TWrapperHandlerCallable = TypeVar("TWrapperHandlerCallable", bound=WrapperHandlerCallable)

class ExceptionCallableAsync(Protocol):
    async def __call__(self, exc: Exception, **kwargs: Any) -> Union[Any, Literal[False]]:
        ...
TExceptionCallableAsync = TypeVar("TExceptionCallableAsync", bound=ExceptionCallableAsync)

class WrapperExceptionCallable(Protocol):
    def __call__(self, func: ExceptionCallableAsync) -> ExceptionCallableAsync:
        ...
TWrapperExceptionCallable = TypeVar("TWrapperExceptionCallable", bound=WrapperExceptionCallable)

CommonCallableAny = Union[
    CommonCallable,
    CommonCallableAsync
]
TCommonCallableAny = TypeVar("TCommonCallableAny", bound=CommonCallableAny)


