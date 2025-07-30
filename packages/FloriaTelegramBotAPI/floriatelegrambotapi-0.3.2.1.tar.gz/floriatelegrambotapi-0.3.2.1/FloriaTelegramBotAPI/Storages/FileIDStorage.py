from typing import Optional
import os

from .. import Utils
from . import FileStorage


class Storage:
    def __init__(self, storage: Optional[FileStorage[str]] = None, save_interval: int = 5):
        self._storage: FileStorage[str] = storage or FileStorage('image_id_storage.json')
        
        Utils.AddEvery(save_interval, self.Save)
    
    def Register(self, path: str, id: str) -> str:   
        self._storage[os.path.abspath(path)] = id
        return id

    def Get(self, path: str) -> Optional[str]:
        return self._storage.Get(os.path.abspath(path), None)

    def Save(self):
        self._storage.Save(indent=True)