from . import Validator, Types


def GetUser(obj: Types.UpdateObject) -> Types.User:
    if isinstance(obj, Types.Message):
        return Validator.IsNotNone(obj.from_user)
    
    elif isinstance(obj, Types.CallbackQuery):
        return obj.from_user
    
    raise ValueError()


def GetChat(obj: Types.UpdateObject) -> Types.Chat:
    if isinstance(obj, Types.Message):
        return obj.chat
    
    elif isinstance(obj, Types.CallbackQuery):
        return Validator.IsNotNone(obj.message).chat
    
    raise ValueError()

