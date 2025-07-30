class Path:
    def __init__(self, path: str):
        self._path: str = path
    
    @property
    def path(self) -> str:
        return self._path