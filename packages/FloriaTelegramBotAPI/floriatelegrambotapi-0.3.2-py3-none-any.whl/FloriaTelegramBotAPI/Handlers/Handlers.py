from typing import Any, cast

from .BaseHandler import Handler
from .. import Utils, Types, SmartTypes
from ..Bot import Bot


class MessageHandler(Handler):
    async def Invoke(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        if isinstance(obj, Types.Message):
            return await super().Invoke(obj, **kwargs)
        return False

    def GetPassedByType(self, obj: Types.UpdateObject, **kwargs: Any) -> list[Any]:
        bot: Bot = kwargs['bot']
        msg: Types.Message = cast(Types.Message, obj)
        return super().GetPassedByType(obj, **kwargs) + [
            Utils.LazyObject(SmartTypes.Message, lambda: SmartTypes.Message(bot, msg)),
            Utils.LazyObject(
                SmartTypes.CommandArgs, 
                lambda: SmartTypes.CommandArgs(
                    msg.text.split(' ')[1:]
                    if msg.text is not None and len(msg.text) > 0 and msg.text[0] == '/' else 
                    []
                )
            )
        ]

class CallbackHandler(Handler):
    async def Invoke(self, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        if isinstance(obj, Types.CallbackQuery):
            return await super().Invoke(obj, **kwargs)
        return False
    
    async def PostInvoke(self, result: bool, obj: Types.UpdateObject, **kwargs: Any) -> bool:
        bot: Bot = kwargs['bot']
        await bot.AnswerCallbackQuery(
            callback_query_id=cast(Types.CallbackQuery, obj).id
        )
        return result
    
    def GetPassedByType(self, obj: Types.UpdateObject, **kwargs: Any) -> list[Any]:
        bot: Bot = kwargs['bot']
        return super().GetPassedByType(obj, **kwargs) + [
            obj,
            Utils.MapOptional(
                cast(Types.CallbackQuery, obj).message, 
                lambda msg: Utils.LazyObject(
                    SmartTypes.Message, 
                    lambda: SmartTypes.Message(
                        bot, 
                        msg
                    )
                )
            ),
            Utils.LazyObject(SmartTypes.CallbackQuery, lambda: SmartTypes.CallbackQuery(bot, cast(Types.CallbackQuery, obj)))
        ]
    

