from typing import Optional
import json

from .... import Utils, Types


def InlineButton(
    text: str,
    callback_data: Optional[Types.JSON_TYPES] = None,
    copy_text: Optional[str] = None,
    url: Optional[str] = None,
    web_app: Optional[str] = None,
    login_url: Optional[Types.LoginUrl] = None,
    switch_inline_query: Optional[str] = None,
    switch_inline_query_current_chat: Optional[str] = None,
    switch_inline_query_chosen_chat: Optional[Types.SwitchInlineQueryChosenChat] = None,
    callback_game: Optional[str] = None,
    pay: Optional[bool] = None,
) -> Types.InlineKeyboardButton:
    return Types.InlineKeyboardButton(
        text=text,
        callback_data=
        Utils.MapOptional(
            callback_data, 
            lambda data: json.dumps(data, separators=(',',':'))
        ),
        url=url,
        web_app=Utils.MapOptional(web_app, lambda data: Types.WebAppInfo(url=data)),
        login_url=login_url,
        switch_inline_query=switch_inline_query,
        switch_inline_query_current_chat=switch_inline_query_current_chat,
        switch_inline_query_chosen_chat=switch_inline_query_chosen_chat,
        copy_text=Utils.MapOptional(copy_text, lambda data: Types.CopyTextButton(text=data)),
        callback_game=callback_game,
        pay=pay
    )