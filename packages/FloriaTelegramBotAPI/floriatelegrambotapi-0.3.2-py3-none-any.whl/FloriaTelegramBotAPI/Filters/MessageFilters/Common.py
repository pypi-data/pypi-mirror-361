from typing import Type, Any, Literal, cast
from enum import Enum
import re

from ... import Validator, Abc, Types


class IsMessage(Abc.Filter):
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        return isinstance(obj, Types.Message)


class IsCommand(IsMessage):
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        if not await super().Check(obj, **kwargs):
            return False
        
        msg = cast(Types.Message, obj)
        
        return msg.text is not None and len(msg.text) > 0 and msg.text[0] == '/'


class Command(IsCommand):
    def __init__(self, *commands: str, lower: bool = True):
        super().__init__()
        
        verified_commands: list[str] = Validator.List(commands, str, subclass=False)
        
        self._commands: list[str] = [*map(lambda command: command.lower(), verified_commands)] if lower else verified_commands
        self._lower = lower
        
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        if not await super().Check(obj, **kwargs):
            return False
        
        msg = cast(Types.Message, obj)
        command = cast(str, msg.text).split(' ')[0][1:]
        
        return (command.lower() if self._lower else command) in self._commands


class InSequence(IsMessage):
    def __init__(self, *items: str, lower: bool = True):
        super().__init__()
        self._items: list[str] = [
            item.lower()
            for item in items
        ] if lower else [*items]
        self._lower: bool = lower
    
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        msg = cast(Types.Message, obj)
        return await super().Check(obj, **kwargs) and msg.text is not None and (msg.text.lower() if self._lower else msg.text) in self._items


class InEnum(InSequence):
    def __init__(self, *enums: Type[Enum], by_keys: bool = False, lower: bool = True):
        items: list[str] = []
        for enum in Validator.List(enums, Type[Enum]):
            items += [
                key if by_keys else value.value
                for key, value in enum._member_map_.items()
            ]
        super().__init__(*items, lower=lower)


class Regex(IsMessage):
    def __init__(self, pattern: str):
        super().__init__()
        Validator.IsInstance(pattern, str)
        self._pattern: str = pattern
    
    async def Check(self, obj: Types.UpdateObject, **kwargs: Any) -> Any | Literal[False]:
        msg = cast(Types.Message, obj)
        return await super().Check(obj, **kwargs) and msg.text is not None and re.fullmatch(self._pattern, msg.text) is not None