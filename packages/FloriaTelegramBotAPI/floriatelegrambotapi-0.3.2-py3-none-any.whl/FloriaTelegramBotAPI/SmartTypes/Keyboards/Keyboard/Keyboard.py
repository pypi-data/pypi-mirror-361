from typing import Optional

from .... import Utils, Validator, Types

from ..NewLine import NewLine


class RemoveKeyboard(Types.ReplyKeyboardRemove): pass

class Keyboard:
    def __init__(
        self, 
        *buttons: Types.KeyboardButton, 
        
        is_persistent: Optional[bool] = None,
        resize: Optional[bool] = None,
        one_time: Optional[bool] = None,
        input_field_placeholder: Optional[str] = None,
        selective: Optional[bool] = None,
    ):
        self.is_persistent: Optional[bool] = is_persistent
        self.resize: Optional[bool] = resize
        self.one_time: Optional[bool] = one_time
        self.input_field_placeholder: Optional[str] = input_field_placeholder
        self.selective: Optional[bool] = selective
    
        self.rows: list[list[Types.KeyboardButton]] = []
        
        if buttons: self.Add(*Validator.List(buttons, Types.KeyboardButton))
    
    def Add(self, *buttons: Types.KeyboardButton):
        row: list[Types.KeyboardButton] = []
        for button in buttons:
            if issubclass(button.__class__, NewLine):
                self.rows.append([*row])
                row.clear()
            else:
                row.append(button)
        if row:
            self.rows.append([*row])
    
    def As_Markup(self) -> Types.ReplyKeyboardMarkup:
        return Types.ReplyKeyboardMarkup(
            **Utils.RemoveValues(
                Utils.ToDict(
                    keyboard=[
                        [
                            button
                            for button in row
                        ]
                        for row in self.rows
                    ],
                    is_persistent=self.is_persistent,
                    resize_keyboard=self.resize,
                    one_time_keyboard=self.one_time,
                    input_field_placeholder=self.input_field_placeholder,
                    selective=self.selective
                ),
                None
            )
        )