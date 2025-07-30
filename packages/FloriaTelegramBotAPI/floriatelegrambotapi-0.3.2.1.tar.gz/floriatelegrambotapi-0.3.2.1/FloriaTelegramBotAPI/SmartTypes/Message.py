from typing import Literal, Optional, Union, Any

from .. import Types, Utils, Enums, Validator
from ..Bot import Bot
from ..Types.Path import Path
from .Keyboards.InlineKeyboard import InlineKeyboard
from .Keyboards.Keyboard import Keyboard


class Message:
    def __init__(self, bot: 'Bot', message: Types.MaybeInaccessibleMessage):
        Validator.IsInstance(bot, Bot)
        Validator.IsInstance(message, Types.Message)
        
        self.bot: Bot = bot
        self.origin: Types.MaybeInaccessibleMessage = message
    
    @staticmethod
    def _ToReplyParameters(
        obj: Optional[Union[
            Types.Message,
            'Message',
            Types.ReplyParameters
        ]]
    ) -> Optional[Types.ReplyParameters]:
        if obj is None or isinstance(obj, Types.ReplyParameters):
            return obj
        
        if isinstance(obj, Types.Message):
            return Types.ReplyParameters(
                message_id=obj.message_id,
                chat_id=obj.chat.id
            )
        
        else: # elif isinstance(obj, Message):
            return Types.ReplyParameters(
                message_id=obj.id,
                chat_id=obj.chat.id
            )
        
    @staticmethod
    def _AsMarkup(
        obj: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply,
            Keyboard,
            InlineKeyboard
        ]]
    ) -> Optional[Union[
        Types.InlineKeyboardMarkup,
        Types.ReplyKeyboardMarkup,
        Types.ReplyKeyboardRemove,
        Types.ForceReply,
    ]]:
        if isinstance(obj, Keyboard | InlineKeyboard):
            return obj.As_Markup()
        return obj
        
    async def Send(
        self,
        text: str,
        reply: Optional[Union[
            Types.Message,
            'Message',
            Types.ReplyParameters
        ]] = None,
        markup: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply,
            Keyboard,
            InlineKeyboard
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
    ) -> 'Message': 
        kwargs.update(
            {
                **Utils.RemoveKeys(locals(), 'self', 'kwargs', 'reply', 'markup'),
                'chat_id': self.chat.id,
                'reply_parameters': self._ToReplyParameters(reply),
                'reply_markup': self._AsMarkup(markup) 
            }
        )
        
        return Message(self.bot, await self.bot.SendMessage(**kwargs))
    
    async def Answer(
        self,
        text: str,
        markup: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply,
            Keyboard,
            InlineKeyboard
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
    ) -> 'Message':
        kwargs.update(
            {
                **Utils.RemoveKeys(locals(), 'self', 'kwargs'),
                'reply': Types.ReplyParameters(
                    message_id=self.id,
                    chat_id=self.chat.id
                ),
                # 'reply_markup': self._AsMarkup(markup)  
            }
        )
        
        return await self.Send(**kwargs)

    async def EditText(
        self,
        text: str,
        markup: Optional[Union[
            Types.InlineKeyboardMarkup, 
            InlineKeyboard
        ]] = None,
        parse_mode: Optional[Enums.ParseMode] = None,
        business_connection_id: Optional[str] = None,
        entities: Optional[list[Types.MessageEntity]] = None,
        link_preview_options: Optional[Types.LinkPreviewOptions] = None,
        **kwargs: Any
    ):
        kwargs.update(
            {
                **Utils.RemoveKeys(locals(), 'self', 'kwargs', 'markup'),
                'chat_id': self.chat.id,
                'message_id': self.id,
                'reply_markup': self._AsMarkup(markup)  
            }
        )
        
        return await self.bot.EditMessageText(**kwargs)

    async def SendPhoto(
        self,
        photo: str | Path,
        caption: Optional[str] = None,
        markup: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply,
            Keyboard,
            InlineKeyboard
        ]] = None,
        reply: Optional[Union[
            Types.Message,
            'Message',
            Types.ReplyParameters
        ]] = None,
        parse_mode: Optional[Enums.ParseMode] = None,
        caption_entities: Optional[list[Types.MessageEntity]] = None,
        show_caption_above_media: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        **kwargs: Any
    ) -> 'Message':
        kwargs.update(
            {
                **Utils.RemoveKeys(locals(), 'self', 'kwargs', 'reply', 'markup'),
                'chat_id': self.chat.id,
                'reply_parameters': self._ToReplyParameters(reply),
                'reply_markup': self._AsMarkup(markup)  
            }
        )
        
        return Message(self.bot, await self.bot.SendPhoto(**kwargs))
    
    async def SendDice(
        self,
        emoji: Optional[Union[
            Literal['🎲', '🎯', '🏀', '⚽', '🎳', '🎰'],
            str
        ]] = None,
        markup: Optional[Union[
            Types.InlineKeyboardMarkup,
            Types.ReplyKeyboardMarkup,
            Types.ReplyKeyboardRemove,
            Types.ForceReply,
            Keyboard,
            InlineKeyboard
        ]] = None,
        reply: Optional[Union[
            Types.Message,
            'Message',
            Types.ReplyParameters
        ]] = None,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        **kwargs: Any
    ) -> 'Message':
        kwargs.update({
            **Utils.RemoveKeys(locals(), 'self', 'kwargs', 'reply', 'markup'),
            'chat_id': self.chat.id,
            'reply_parameters': self._ToReplyParameters(reply),
            'reply_markup': self._AsMarkup(markup)  
        })
        
        return Message(self.bot, await self.bot.SendDice(**kwargs))
    
    @property
    def text(self) -> Optional[str]:
        if isinstance(self.origin, Types.Message):
            return self.origin.text
        return None
    
    @property
    def chat(self):
        return self.origin.chat
    
    @property
    def from_user(self) -> Optional[Types.User]:
        if isinstance(self.origin, Types.Message):
            return self.origin.from_user
        return None
    
    @property
    def id(self):
        return self.origin.message_id
    
    
    