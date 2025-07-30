from typing import Type, Any, Callable, TypeVar, get_args, get_origin, Union, Iterable, Optional
import inspect


T = TypeVar('T')
T2 = TypeVar('T2')


def _GetArgsOfType(type: Type[Any]) -> tuple[Type[Any]]:
    if get_origin(type) is Union:
        return get_args(type)
    return (type,)

def IsSubClass(data: Type[Any], type: Type[T], *, safe: bool = False) -> bool:
    for cur_type in _GetArgsOfType(type):
        if issubclass(data, cur_type):
            return True
    if safe:
        return False
    raise ValueError()

def IsInstance(data: Any, type: Type[T], *, safe: bool = False) -> bool:
    for cur_type in _GetArgsOfType(type):
        if isinstance(data, cur_type):
            return True
    if safe:
        return False
    raise ValueError()

def List(data: Iterable[Any], *types: Type[T], subclass: bool = True) -> list[T]:
    for item in data:
        if subclass:
            if not any(
                issubclass(type(item), t) 
                for t in types 
            ):
                raise ValueError()
        else:
            if not any(
                isinstance(item, t) 
                for t in types
            ):
                raise ValueError()
    return list(data)

# def List(data: Iterable[Any], type: Type[T], *, subclass: bool = True) -> list[T]:
#     for item in data:
#         if subclass and not IsSubClass(item, type, safe=True) or not subclass and not IsInstance(item, type, safe=True):
#             raise ValueError()
#     return [*data]

def ListSubClassTypes(data: Iterable[Type[Any]], type: Type[T]) -> list[Type[T]]:
    for item in data:
        if IsSubClass(item, type, safe=True):
            raise ValueError()
    return [*data]

def ByFunc(func: Callable[[T], bool], data: T) -> T:
    if not func(data):
        raise ValueError()
    return data

def IsCallableAsync(
    func: T,
) -> T:
    if not inspect.iscoroutinefunction(func):
        raise ValueError()
    return func

def IsNotNone(
    data: Optional[T]
) -> T:
    if data is None:
        raise ValueError()
    return data