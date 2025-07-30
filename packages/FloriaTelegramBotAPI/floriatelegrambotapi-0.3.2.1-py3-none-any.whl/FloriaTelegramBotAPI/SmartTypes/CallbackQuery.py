from typing import Optional, Any
import json

from .. import Types
from ..Bot import Bot


class CallbackQuery:
    def __init__(self, bot: Bot, query: Types.CallbackQuery):
        self.bot: Bot = bot
        self.origin = query
        
        self._validated_data: Optional[Any] = None
    
    @property
    def data(self) -> Optional[str]:
        return self.origin.data
    
    @property
    def valdata(self) -> Optional[Types.JSON_TYPES]:
        if self.data is None:
            return None
        
        if self._validated_data is None:
            self._validated_data = json.loads(self.data)
            
        return self._validated_data