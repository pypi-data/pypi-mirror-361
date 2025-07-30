import json
from typing import Union, Optional, Any, Callable, Type, get_args, get_origin, TypeVar, cast, Literal
from types import UnionType
from pydantic import BaseModel
import inspect
import os
from . import Protocols, Types
import schedule


T = TypeVar("T")
T2 = TypeVar("T2")


def RemoveKeys(data: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {
        key: value 
        for key, value in data.items()
        if key not in keys
    }

def RemoveValues(data: dict[str, Any], *values: Any) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value not in values
    }

def ToDict(**kwargs: Any) -> dict[str, Any]:
    return kwargs

def ConvertToJson(
    obj: Types.PRIMITIVE_VALUES
) -> Types.JSON_TYPES:
    if isinstance(obj, dict):
        return {
            key: ConvertToJson(value)
            for key, value in obj.items()
        }
    
    elif isinstance(obj, list):
        return [
            ConvertToJson(value) 
            for value in obj
        ]
    
    elif issubclass(obj.__class__, BaseModel):
        return cast(BaseModel, obj).model_dump(mode='json', exclude_none=True)
    
    elif isinstance(obj, Union[str, int, float, bool]) or obj in [None]:
        return obj
    
    raise RuntimeError('Unsupport type')

def GetPathToObject(obj: Any) -> str:
    return f'File "{os.path.abspath(inspect.getfile(obj))}", line {inspect.getsourcelines(obj)[1]}'

def MapOptional(data: Optional[T], func: Callable[[T], T2]) -> Optional[T2]:
    return None if data is None else func(data)

class LazyObject:
    def __init__(self, returning_type: Type[Any], func: Protocols.Functions.CommonCallable, *args: Any, **kwargs: Any):
        self.type: Type[Any] = returning_type
        self.func: Protocols.Functions.CommonCallable = func
        self.args = args
        self.kwargs = kwargs
    
    def Get(self):
        return self.func(*self.args, **self.kwargs)

# TODO: Разобраться в функции, оптимизировать
async def InvokeFunction(
    func: Protocols.Functions.HandlerCallableAsync[...], 
    *,
    passed_by_name: dict[str, Any] = {}, 
    passed_by_type: list[Any | LazyObject] = []
) -> Any:
    # 1. Собираем доступные типы в словарь
    type_candidates: dict[Type[Any], Any | LazyObject] = {
        type(None): None
    }
    
    for value in passed_by_type:
        if value is None:
            continue
            
        if isinstance(value, LazyObject):
            # Регистрируем основной тип и его origin (если есть)
            type_candidates[value.type] = value
            origin = get_origin(value.type)
            if origin is not None:
                type_candidates[origin] = value
        else:
            # Регистрируем конкретный тип и его origin
            obj_type: Type[Any] = cast(Type[Any], type(value))
            type_candidates[obj_type] = value
            origin = get_origin(obj_type)
            if origin is not None:
                type_candidates[origin] = value

    signature = inspect.signature(func)
    kwargs = passed_by_name.copy()
    errors: list[str] = []
    
    for param_name, param in signature.parameters.items():
        if param_name in kwargs:
            continue
            
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
            
        ann = param.annotation
        if ann is param.empty:
            errors.append(f"'{param_name}' is missing type annotation")
            continue
            
        candidate_types: set[Any] = set()
        
        if get_origin(ann) is Union or isinstance(ann, UnionType):
            candidate_types.update(get_args(ann))
        else:
            candidate_types.add(ann)
        
        additional_types: set[Any] = set()
        for t in candidate_types:
            origin = get_origin(t)
            if origin is not None:
                additional_types.add(origin)
        candidate_types.update(additional_types)
        
        value = None
        for t in candidate_types:
            if t in type_candidates:
                candidate = type_candidates[t]
                value = candidate.Get() if isinstance(candidate, LazyObject) else candidate
                break
        
        if value is not None:
            kwargs[param_name] = value
        elif param.default is param.empty:
            type_names = [t.__name__ for t in candidate_types]
            errors.append(f"{param_name}: {' | '.join(type_names)}")
    
    if errors:
        available_types = ', '.join(t.__name__ for t in type_candidates)
        error_msg = "\n  - ".join(errors)
        raise RuntimeError(
            f"Missing required arguments:\n  - {error_msg}\n"
            f"Available types: {available_types}"
        )
    
    return await func(**kwargs)

def ExceptionToText(exc: Exception, type: Literal['full', 'only_name'] = 'full') -> str:
    match type:
        case 'full':
            return f'Ошибка {exc.__class__.__name__}{
                f':\n  {'\n  '.join(map(str, exc.args))}' 
                if len(exc.args) > 0 else 
                ''
            }'
        
        case 'only_name':
            return f'Ошибка {exc.__class__.__name__}'
        
        case _:
            raise ValueError()

def FileExists(path: str) -> bool:
    return os.path.exists(path)

def ReadFile(path: str, mode: Union[Literal['r', 'rb'], str] = 'r') -> str | bytes:
    with open(path, mode=mode, encoding='utf-8') as file:
        return file.read()

def WriteFile(path: str, data: Any):
    dir_path = os.path.dirname(path)
    if len(dir_path) > 0 and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        
    with open(path, mode='w', encoding='utf-8') as file:
        file.write(f'{data}')

def ReadJson(path: str) -> Types.JSON_TYPES:
    return json.loads(ReadFile(path))

def WriteJson(path: str, data: Types.JSON_TYPES):
    WriteFile(path, json.dumps(data))
    
def AddEvery(seconds: int, func: Protocols.Functions.CommonCallable, *args: Any, **kwargs: Any):
    schedule.every(seconds).seconds.do(func, *args, **kwargs) # type: ignore

def Every(
    seconds: int
) -> Protocols.Functions.WrappedCommonCallable:
    def wrapper(func: Protocols.Functions.CommonCallable) -> Protocols.Functions.CommonCallable:
        AddEvery(seconds, func)
        return func
    return wrapper

