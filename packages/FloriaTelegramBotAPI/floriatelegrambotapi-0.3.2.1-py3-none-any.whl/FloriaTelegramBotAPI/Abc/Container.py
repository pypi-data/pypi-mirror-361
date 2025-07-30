from typing import Generic, Any
from abc import ABC, abstractmethod
from ..Utils import T


class Container(ABC, Generic[T]):
    @abstractmethod
    def Register(self, *args: Any, **kwargs: Any) -> Any:    
        ...
    
    @abstractmethod
    async def Invoke(self, *args: Any, **kwargs: Any) -> Any:
        ...
    
    @abstractmethod
    def __len__(self) -> int:
        ...
        
        
    

