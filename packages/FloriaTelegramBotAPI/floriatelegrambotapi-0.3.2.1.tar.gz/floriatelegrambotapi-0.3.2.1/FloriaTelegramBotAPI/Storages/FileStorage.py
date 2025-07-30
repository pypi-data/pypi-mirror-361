import json
from typing import Generic, Optional, Type, cast
from pydantic import BaseModel

from ..Abc.Storage import TStorageValue
from ..Types import KEY_TYPES
from .. import Utils

from .MemoryStorage import MemoryStorage


class FileStorage(MemoryStorage[TStorageValue], Generic[TStorageValue]):
    def __init__(self, filename: str, model: Optional[Type[TStorageValue]] = None):
        super().__init__()
        
        self._filename: str = filename
        self._model: Optional[Type[TStorageValue]] = model
        
        self._memory: dict[KEY_TYPES, TStorageValue] = {}
        self.Load()

    def Load(self):
        if not Utils.FileExists(self._filename):
            return
        
        data = Utils.ReadJson(self._filename)
        if not isinstance(data, dict):
            raise 
        
        self._memory.update(
            cast(
                dict[KEY_TYPES, TStorageValue],
                {
                    key: 
                        self._model(**value) 
                        if self._model is not None and issubclass(self._model, BaseModel) else 
                        value
                    for key, value in data.items()
                }
            )
        )
    
    def Save(self, indent: bool = False):
        Utils.WriteFile(
            self._filename,
            json.dumps(
                {
                    f'{key}': Utils.ConvertToJson(value)
                    for key, value in self._memory.items()
                },
                indent=2 if indent else None
            )
        )
    
    def Set(self, key: KEY_TYPES, value: TStorageValue) -> KEY_TYPES:
        return super().Set(key, value)