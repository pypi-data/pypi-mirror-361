import httpx
from typing import Any, Optional
import json

from .Config import Config
from . import Utils, Protocols


class WebClient:
    def __init__(self, token: str, config: Config):
        self.__token = token
        self._config: Config = config
        
        self._client = httpx.AsyncClient(timeout=self.config.timeout)
    
    async def GetUpdates(self, update_offset: int) -> list[dict[str, Any]]:
        return (await self.RequestGet(
            'getUpdates', 
            {
                'offset': update_offset + 1
            }
        )).get('result', [])
    
    async def MakeRequest(
        self, 
        method: Protocols.Functions.CommonCallableAsync, 
        command: str,
        **kwargs: Any
    ) -> dict[str, Any]:
        for attempt in range(self.config.retry_count):
            try:
                response: httpx.Response = await method(
                    url=f'https://api.telegram.org/bot{self.__token}/{command}',
                    **kwargs
                )
                
                data: dict[str, Any] = response.json()
                if not response.is_success:
                    raise Exception(
                        f"\n\tCode: {data.get('error_code')}"
                        f"\n\tDescription: {data.get('description')}"
                        f"\n\tCommand: {command}"
                        f"\n\tRequest: \n{json.dumps(json.loads(response.request.content.decode()), indent=4)}"
                    )
                    
                return data
            
            except Exception as ex:
                if attempt == self.config.retry_count - 1:
                    raise httpx.RequestError(
                        f'Failed after {self._config.retry_count} attempts: {str(ex)}'
                    ) from ex
        
        raise httpx.RequestError(f'Failed to complete request after {self.config.retry_count} attempts')
        
    async def RequestGet(
        self, 
        command: str, 
        data: Optional[Any] = None
    ) -> dict[str, Any]:
        return await self.MakeRequest(
            self._client.get, 
            command,
            
            params=Utils.ConvertToJson(data or {})
        )
    
    async def RequestPost(
        self, 
        command: str, 
        data: Any,
    ) -> dict[str, Any]:
        return await self.MakeRequest(
            self._client.post, 
            command,
            
            json=Utils.ConvertToJson(data or {}),
        )
    
    async def RequestPostData(
        self,
        command: str,
        data: Any,
        files: Any = None
    ) -> dict[str, Any]:
        return await self.MakeRequest(
            self._client.post,
            command,
            
            data=Utils.ConvertToJson(data or {}),
            files=files
        )
    
    @property
    def config(self) -> Config:
        return self._config