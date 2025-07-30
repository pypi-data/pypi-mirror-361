from typing import Generic, Iterator, Optional, TypeVar, AsyncIterator
from abc import ABC, abstractmethod

from ..Types import KEY_TYPES, PRIMITIVE_VALUES


TStorageValue = TypeVar('TStorageValue', bound=PRIMITIVE_VALUES)
class Storage(ABC, Generic[TStorageValue]):
    @abstractmethod
    def Get(self, key: KEY_TYPES, default: Optional[TStorageValue] = None) -> Optional[TStorageValue]: ...
    
    @abstractmethod
    def Set(self, key: KEY_TYPES, value: TStorageValue) -> KEY_TYPES: ...
    
    @abstractmethod
    def Pop(self, key: KEY_TYPES, default: Optional[TStorageValue] = None) -> Optional[TStorageValue]: ... 
    
    @abstractmethod
    def Has(self, key: KEY_TYPES) -> bool: ...
    
    @abstractmethod
    def __iter__(self) -> Iterator[KEY_TYPES]: ...



    def __contains__(self, key: KEY_TYPES) -> bool:
        return self.Has(key)
    
    def __getitem__(self, key: KEY_TYPES) -> TStorageValue:
        data = self.Get(key)
        if data is None:
            raise KeyError()
        return data
    
    def __setitem__(self, key: KEY_TYPES, value: TStorageValue) -> KEY_TYPES:
        return self.Set(key, value)
    
    def __delitem__(self, key: KEY_TYPES) -> Optional[TStorageValue]:
        return self.Pop(key)

class StorageAsync(ABC, Generic[TStorageValue]):
    @abstractmethod
    async def Get(self, key: KEY_TYPES, default: Optional[TStorageValue] = None) -> Optional[TStorageValue]: ...
    
    @abstractmethod
    async def Set(self, key: KEY_TYPES, value: TStorageValue) -> KEY_TYPES: ...
    
    @abstractmethod
    async def Pop(self, key: KEY_TYPES, default: Optional[TStorageValue] = None) -> Optional[TStorageValue]: ... 
    
    @abstractmethod
    async def Has(self, key: KEY_TYPES) -> bool: ...
    
    @abstractmethod
    async def __aiter__(self) -> AsyncIterator[KEY_TYPES]: ...

