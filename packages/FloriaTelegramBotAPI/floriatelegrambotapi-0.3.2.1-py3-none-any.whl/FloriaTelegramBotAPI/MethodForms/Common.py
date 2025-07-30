from pydantic import BaseModel
from typing import Optional, Union

from FloriaTelegramBotAPI.Types.Common import ReplyParameters

from .. import Enums, Types


class SendMessage(BaseModel):
    chat_id: str | int
    text: str
    reply_parameters: Optional[Types.ReplyParameters] = None
    reply_markup: Optional[Union[
        Types.InlineKeyboardMarkup,
        Types.ReplyKeyboardMarkup,
        Types.ReplyKeyboardRemove,
        Types.ForceReply
    ]] = None
    parse_mode: Optional[Enums.ParseMode] = None
    business_connection_id: Optional[str] = None
    message_thread_id: Optional[int] = None
    entities: Optional[list[Types.MessageEntity]] = None
    link_preview_options: Optional[Types.LinkPreviewOptions] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    allow_paid_broadcast: Optional[bool] = None
    message_effect_id: Optional[str] = None


class SendChatAction(BaseModel):
    chat_id: str | int
    action: Enums.Action
    business_connection_id: Optional[str] = None
    message_thread_id: Optional[int] = None


class SendPhoto(BaseModel):
    chat_id: str | int
    photo: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[Enums.ParseMode] = None
    caption_entities: Optional[list[Types.MessageEntity]] = None
    show_caption_above_media: Optional[bool] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    allow_paid_broadcast: Optional[bool] = None
    message_effect_id: Optional[str] = None
    reply_parameters: Optional[Types.ReplyParameters] = None
    reply_markup: Optional[Union[
        Types.InlineKeyboardMarkup,
        Types.ReplyKeyboardMarkup,
        Types.ReplyKeyboardRemove,
        Types.ForceReply
    ]] = None
    business_connection_id: Optional[str] = None
    message_thread_id: Optional[int] = None


class AnswerCallbackQuery(BaseModel):
    callback_query_id: str
    text: Optional[str] = None
    show_alert: Optional[bool] = None
    url: Optional[str] = None
    cache_time: Optional[int] = None


class EditMessageText(BaseModel):
    text: str
    chat_id: Optional[str | int] = None
    reply_markup: Optional[Types.InlineKeyboardMarkup] = None
    parse_mode: Optional[Enums.ParseMode] = None
    business_connection_id: Optional[str] = None
    message_id: Optional[int] = None
    inline_message_id: Optional[str] = None
    entities: Optional[list[Types.MessageEntity]] = None
    link_preview_options: Optional[Types.LinkPreviewOptions] = None
    
class SendDice(BaseModel):
    chat_id: str | int
    business_connection_id: Optional[str] = None
    message_thread_id: Optional[int] = None
    emoji: Optional[str] = None
    disable_notification: Optional[bool] = None
    protect_content: Optional[bool] = None
    allow_paid_broadcast: Optional[bool] = None
    message_effect_id: Optional[str] = None
    reply_parameters: Optional[ReplyParameters] = None
    reply_markup: Optional[Union[
        Types.InlineKeyboardMarkup,
        Types.ReplyKeyboardMarkup,
        Types.ReplyKeyboardRemove,
        Types.ForceReply
    ]] = None
    
    
    