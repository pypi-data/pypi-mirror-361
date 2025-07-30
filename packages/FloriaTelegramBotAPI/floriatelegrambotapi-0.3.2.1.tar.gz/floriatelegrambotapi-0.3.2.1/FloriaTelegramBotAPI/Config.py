import logging
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta

from .Enums import ParseMode


class Config(BaseModel):
    
    # connection
    timeout: float = 5
    retry_count: int = 5
    
    # name
    name_max_length: int = 18
    
    # log
    log_format: str = '[%(levelname)s] - %(name)s - %(message)s'
    log_file: Optional[str] = None
    stream_handler_level: int = logging.INFO
    file_handler_level: int = logging.WARNING
    
    # settings
    parse_mode: Optional[ParseMode] = None
    disable_notification: Optional[bool] = None
    
    
    # feature
    common_storage_save_interval: int = 60
    
    callback_length_fix: str | bool = False
    callback_data_life_time: int | timedelta = timedelta(minutes=20)
    callback_data_storage_save_interval: Optional[int] = None
    
    file_cache: bool = False
    file_cache_storage_save_interval: Optional[int] = None
    
    
        