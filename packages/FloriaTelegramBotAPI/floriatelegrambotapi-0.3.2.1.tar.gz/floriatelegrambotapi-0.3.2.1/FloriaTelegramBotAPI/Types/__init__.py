from typing import TypeVar, Union, Type, TypedDict
from uuid import UUID

from .Common import *
from .Path import Path


UpdateObject = Union[
    Message,
    CallbackQuery,
    Type[None]
]

TUpdateObject = TypeVar("TUpdateObject", bound=UpdateObject)
TUpdateObject_co = TypeVar("TUpdateObject_co", bound=UpdateObject, covariant=True)

KEY_TYPES = Union[
    str
]

JSON_TYPES = Union[
    dict[str, 'JSON_TYPES'],
    TypedDict,
    list['JSON_TYPES'],
    str,
    int,
    float,
    bool,
    None,
]

PRIMITIVE_VALUES = Union[
    JSON_TYPES,
    BaseModel
]
