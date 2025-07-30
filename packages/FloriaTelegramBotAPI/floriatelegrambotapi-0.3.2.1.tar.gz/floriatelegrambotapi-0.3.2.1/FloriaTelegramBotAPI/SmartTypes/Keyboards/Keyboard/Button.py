from typing import Optional

from .... import Types


def Button(
    text: str,
    request_contact: Optional[bool] = None,
    request_location: Optional[bool] = None,
    request_users: Optional[Types.KeyboardButtonRequestUsers] = None,
    request_chat: Optional[Types.KeyboardButtonRequestChat] = None,
    request_poll: Optional[Types.KeyboardButtonPollType] = None,
    web_app: Optional[Types.WebAppInfo] = None,
) -> Types.KeyboardButton:
    return Types.KeyboardButton(
        text=text,
        request_users=request_users,
        request_chat=request_chat,
        request_contact=request_contact,
        request_location=request_location,
        request_poll=request_poll,
        web_app=web_app
    )
