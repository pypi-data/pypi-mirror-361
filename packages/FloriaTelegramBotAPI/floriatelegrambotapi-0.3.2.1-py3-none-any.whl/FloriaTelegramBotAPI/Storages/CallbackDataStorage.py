from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import mmh3

from FloriaTelegramBotAPI import Exceptions
from .. import Utils
from . import FileStorage


class RecordData(BaseModel):
    data: str
    expires_at: datetime


class Storage:
    def __init__(self, storage: Optional[FileStorage[RecordData]] = None, save_interval: int = 5):
        self._storage: FileStorage[RecordData] = storage or FileStorage('callback_data_storage.json', RecordData)
        
        Utils.AddEvery(save_interval, self.Save)
    
    def Register(self, data: str, life_time: timedelta = timedelta(minutes=20)) -> str:       
        token = mmh3.hash_bytes(data).hex()
        self._storage[token] = RecordData(
            data=data,
            expires_at=datetime.now() + life_time
        )
        return token

    def Get(self, token: str) -> str:
        try:
            record = self._storage[token]
            if record.expires_at <= datetime.now():
                self._storage.Pop(token)
                
            return record.data
        
        except KeyError:
            raise Exceptions.CallbackStorageTokenNotFoundError()
    
    def Clear(self, all: bool = False):
        now = datetime.now()
        for key, value in self._storage.Items():
            if all or value.expires_at <= now:
                self._storage.Pop(key)
    
    def Save(self):
        self.Clear()
        self._storage.Save(indent=True)