import asyncio
from datetime import timedelta
from typing import Optional, Any, Union
import logging
import schedule

from .Router import Router
from .Config import Config
from .Events import Event
from . import Types, Abc, Enums, Utils, MethodForms
from .WebClient import WebClient
from . import Protocols, Validator
from .Storages import FileIDStorage, FileStorage, CallbackDataStorage


class Bot(Router):
    def __init__(self, token: str, config: Optional[Config] = None):
        super().__init__()
        
        self._on_start_event: Event[Protocols.Functions.CommonCallableAny] = Event()
        self._on_stop_event: Event[Protocols.Functions.CommonCallableAny] = Event()
        
        self._config = config or Config()
        
        self._logger: Optional[logging.Logger] = None
        self._info: Optional[Types.User] = None
        self._enabled: bool = True
        
        self._update_offset: int = 0
        
        self._client: WebClient = WebClient(token, self._config)
        
        self._callback_data_storage: Optional[CallbackDataStorage.Storage] = None
        self._file_id_storage: Optional[FileIDStorage.Storage] = None
        
    def Run(
        self, 
        *, 
        skip_updates: bool = False,
        **kwargs: Any
    ):
        kwargs.update(Utils.RemoveKeys(locals(), 'kwargs', 'self'))
        
        asyncio.run(
            self.Polling(
                **kwargs
            )
        )
        
    async def Polling(
        self, 
        *, 
        skip_updates: bool = False
    ):
        self._info = Types.User(**(await self._client.RequestGet('getMe'))['result'])
        
        self._logger = logging.getLogger(
            f'{self.info.username[:self.config.name_max_length]}{'..' if len(self.info.username) > self.config.name_max_length else ''}({self.info.id})'
            if self.info.username is not None else
            f'{self.info.first_name[:self.config.name_max_length]}{'..' if len(self.info.first_name) > self.config.name_max_length else ''}({self.info.id})'
        )
        
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self._config.stream_handler_level)
        stream_handler.setFormatter(logging.Formatter(self._config.log_format))
        self._logger.addHandler(stream_handler)
        
        if self._config.log_file is not None:
            file_handler = logging.FileHandler(self._config.log_file)
            file_handler.setLevel(self._config.file_handler_level)
            file_handler.setFormatter(logging.Formatter(self._config.log_format))
            self._logger.addHandler(file_handler)
        
        self._logger.setLevel(self._config.stream_handler_level)
        
        if self.config.callback_length_fix is not False:
            self._callback_data_storage = CallbackDataStorage.Storage(
                FileStorage(
                    f'Cache/{self.info.id}/callback_data_storage.json'
                    if self.config.callback_length_fix is True else
                    self.config.callback_length_fix,
                    CallbackDataStorage.RecordData
                ),
                self.config.callback_data_storage_save_interval or self.config.common_storage_save_interval
            )
            self._on_stop_event.Register(self._callback_data_storage.Save)
        
        if self.config.file_cache:
            self._file_id_storage = FileIDStorage.Storage(
                FileStorage(
                    f'Cache/{self.info.id}/file_id_storage.json' if self.config.file_cache else self.config.file_cache,
                    str
                ),
                self.config.file_cache_storage_save_interval or self.config.common_storage_save_interval
            )
            self._on_stop_event.Register(self._file_id_storage.Save)
        
        if skip_updates:
            for update in await self._client.GetUpdates(self._update_offset):
                self._update_offset = update.pop('update_id')
        
        asyncio.create_task(self._RunScheduler())
        
        self.logger.info(f'Initialized')
        
        try:
            await self._on_start_event()
            
            while self.enabled:
                schedule.run_pending()
                for update in await self._client.GetUpdates(self._update_offset):
                    await self._ProcessUpdate(update)
            
        except Exception as ex:
            self.logger.critical(ex.__class__.__name__, exc_info=True)
        
        finally:
            await self._on_stop_event()
    
    async def _RunScheduler(self):
        while self.enabled:
            schedule.run_pending()
            await asyncio.sleep(0.5)
    
    def _SetUpdateOffset(self, offset: int):
        self._update_offset = max(self._update_offset, offset)
    
    async def _ProcessUpdate(self, update: dict[str, Any]):
        obj: Optional[Types.UpdateObject] = None
        offset: int = 0
        try:
            offset = update.pop('update_id')
            
            for key, data in update.items():
                obj = self._ParseUpdateObject(key, data)
                if obj is None:
                    continue
                
                await self.Processing(
                    self._PostUpdateObject(obj), 
                    bot=self
                )
        
        except Exception as ex:
            if not (
                len(self._exceptions) > 0 and 
                await self._exceptions.Invoke(ex, obj=obj, bot=self)
            ):
                self.logger.error(ex.__class__.__name__, exc_info=True)
            
        finally:
            self._SetUpdateOffset(offset)
    
    def _ParseUpdateObject(self, key: str, data: dict[str, Any]) -> Optional[Types.UpdateObject]:
        match key:
            case 'message':
                return Types.Message(**data)
            
            case 'callback_query':
                return Types.CallbackQuery(**data)
                
            case _:
                self.logger.warning(f'Unknowed update type: "{key}"')
                return None
    
    def _PostUpdateObject(self, obj: Types.UpdateObject) -> Types.UpdateObject:
        if self._callback_data_storage is not None and isinstance(obj, Types.CallbackQuery) and obj.data is not None:
            obj.data = self._callback_data_storage.Get(obj.data)
        
        return obj
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    def Stop(self):
        self._enabled = False
        
    @property
    def config(self) -> Config:
        return self._config

    @property
    def info(self) -> Types.User:
        return Validator.IsNotNone(self._info)

    @property
    def logger(self) -> logging.Logger:
        return Validator.IsNotNone(self._logger)
    
    def OnStart(self, func: Protocols.Functions.CommonCallableAsync):
        self._on_start_event.Register(func)
        return func
    
    def OnStop(self, func: Protocols.Functions.CommonCallableAsync):
        self._on_stop_event.Register(func)
        return func
    
# ---------
#    API
# ---------
    
    def _ReplaceCallbackData(
        self,
        markup: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply
        ]]
    ) -> Optional[Union[
        Types.InlineKeyboardMarkup,
        Types.ReplyKeyboardMarkup,
        Types.ReplyKeyboardRemove,
        Types.ForceReply
    ]]:
        if not isinstance(markup, Types.InlineKeyboardMarkup) or self._callback_data_storage is None:
            return markup
        
        for row in markup.inline_keyboard:
            for button in row:
                if button.callback_data is None:
                    continue
                
                button.callback_data = self._callback_data_storage.Register(
                    button.callback_data,
                    self.config.callback_data_life_time 
                    if isinstance(self.config.callback_data_life_time, timedelta) else
                    timedelta(seconds=self.config.callback_data_life_time)
                )
        
        return markup
    
    async def SendMessage(
        self,
        chat_id: int,
        text: str,
        reply_parameters: Optional[Types.ReplyParameters] = None,
        reply_markup: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply
        ]] = None,
        parse_mode: Optional[Enums.ParseMode] = None,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        entities: Optional[list[Types.MessageEntity]] = None,
        link_preview_options: Optional[Types.LinkPreviewOptions] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        **kwargs: Any
    ) -> Types.Message: 
        kwargs.update(
            {
                **Utils.RemoveKeys(locals(), 'self', 'kwargs'),
                'parse_mode': parse_mode or self.config.parse_mode,
                'reply_markup': self._ReplaceCallbackData(reply_markup),
                'disable_notification': disable_notification or self.config.disable_notification
            }
        )
        
        return Types.Message(**
            (await self._client.RequestPost(
                'sendMessage', 
                MethodForms.SendMessage(**kwargs)
            ))['result']
        )
    
    async def SendChatAction(
        self,
        chat_id: str | int,
        action: Enums.Action,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        **kwargs: Any
    ):
        kwargs.update(Utils.RemoveKeys(locals(), 'self', 'kwargs'))
        
        await self._client.RequestPost(
            'sendChatAction',
            MethodForms.SendChatAction(**kwargs)
        )
    
    async def SendPhoto(
        self,
        chat_id: str | int,
        photo: str | Types.Path,
        caption: Optional[str] = None,
        parse_mode: Optional[Enums.ParseMode] = None,
        caption_entities: Optional[list[Types.MessageEntity]] = None,
        show_caption_above_media: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        reply_parameters: Optional[Types.ReplyParameters] = None,
        reply_markup: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply
        ]] = None,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        **kwargs: Any
    ) -> Types.Message: 
        kwargs.update({
            **Utils.RemoveKeys(locals(), 'self', 'kwargs', 'photo'),
            'parse_mode': parse_mode or self.config.parse_mode,
            'reply_markup': self._ReplaceCallbackData(reply_markup),
            'disable_notification': disable_notification or self.config.disable_notification
        })
        photo_is_id = isinstance(photo, str)
        file_id_cache: Optional[str] = self._file_id_storage.Get(photo.path) if not photo_is_id and self._file_id_storage is not None else None
        
        if photo_is_id or file_id_cache is not None:
            return Types.Message(**(await self._client.RequestPost(
                'sendPhoto',
                MethodForms.SendPhoto(
                    photo=(photo if photo_is_id else file_id_cache),
                    **kwargs
                )
            ))['result'])
            
        else:
            with open(photo.path, 'rb') as file:
                message = Types.Message(**(await self._client.RequestPostData(
                    'sendPhoto',
                    MethodForms.SendPhoto(**kwargs),
                    {
                        'photo': file
                    }
                ))['result'])
                if self._file_id_storage is not None:
                    self._file_id_storage.Register(photo.path, message.photo[-1].file_id)
                return message
              
    async def AnswerCallbackQuery(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
        cache_time: Optional[int] = None,
        **kwargs: Any
    ):
        kwargs.update(Utils.RemoveKeys(locals(), 'self', 'kwargs'))
        
        await self._client.RequestPost(
            'answerCallbackQuery',
            MethodForms.AnswerCallbackQuery(**kwargs)
        )
    
    async def EditMessageText(
        self,
        text: str,
        chat_id: Optional[str | int] = None,
        reply_markup: Optional[Types.InlineKeyboardMarkup] = None,
        parse_mode: Optional[Enums.ParseMode] = None,
        business_connection_id: Optional[str] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        entities: Optional[list[Types.MessageEntity]] = None,
        link_preview_options: Optional[Types.LinkPreviewOptions] = None,
        **kwargs: Any
    ):
        kwargs.update({
            **Utils.RemoveKeys(locals(), 'self', 'kwargs'),
            'parse_mode': parse_mode or self.config.parse_mode,
            'reply_markup': self._ReplaceCallbackData(reply_markup)
        })
        
        await self._client.RequestPost(
            'editMessageText',
            MethodForms.EditMessageText(**kwargs)
        )
    
    async def SendDice(
        self,
        chat_id: str | int,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        emoji: Optional[str] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        reply_parameters: Optional[Types.ReplyParameters] = None,
        reply_markup: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply,
        ]] = None,
        **kwargs: Any
    ) -> Types.Message: 
        kwargs.update({
            **Utils.RemoveKeys(locals(), 'self', 'kwargs'),
            'reply_markup': self._ReplaceCallbackData(reply_markup),
            'disable_notification': disable_notification or self.config.disable_notification
        })
        
        return Types.Message(**(await self._client.RequestPost(
            'sendDice',
            MethodForms.SendDice(**kwargs)
        ))['result'])