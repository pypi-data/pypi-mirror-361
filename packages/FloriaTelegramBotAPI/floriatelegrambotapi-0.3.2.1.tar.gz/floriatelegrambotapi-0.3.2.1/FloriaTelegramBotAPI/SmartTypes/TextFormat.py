from collections import UserString
from typing import Literal, Union, cast

from ..Enums import ParseMode


class TextFormat(UserString):
    def __init__(
        self, 
        obj: object, 
        *formats: Union[
            Literal[
                'bold', 'b',
                'italic', 'i',
                'underline', 'u',
                'strikethrough', 's',
                'spoiler',
                'link=',
                'user=',
                'pre',
                'code=',
                'blockquote', 'blockquote-expandable'
            ],
            str
        ], 
        parse_mode: ParseMode = ParseMode.HTML, 
        screen_symbols: bool = True
    ):
        self._parse_mode: ParseMode = parse_mode
        obj_text: str = str(obj)
        
        if screen_symbols:
            match self.parse_mode:
                case ParseMode.HTML:
                    screen_obj_text = obj_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                case _:
                    raise ValueError()
        else:
            screen_obj_text = obj_text
        
        for format in formats:
            if '=' in format:
                format_args: list[str] = cast(list[str], format.split('=', format.index('=')))
            else:
                format_args: list[str] = [format]
                
            match format_args[0]:
                case 'bold' | 'b':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Bold()
                
                case 'italic' | 'i':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Italic()
                
                case 'underline' | 'u':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Underline()
                
                case 'strikethrough' | 's':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Strikethrough()
                    
                case 'spoiler':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Spoiler()
                    
                case 'link':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Link(format_args[1])
                
                case 'user':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).LinkUsername(format_args[1])
                    
                case 'pre':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Pre()
                    
                case 'code':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Code(format_args[1])
                    
                case 'blockquote' | 'blockquote-expandable':
                    screen_obj_text = TextFormat(
                        screen_obj_text, parse_mode=self.parse_mode, screen_symbols=False
                    ).Blockquote(expandable=format_args[0] == 'blockquote-expandable')
                    
                case _:
                    raise ValueError()
        
        super().__init__(screen_obj_text)
        
        
    def Bold(self) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<b>{self}</b>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)
    
    def Italic(self) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<i>{self}</i>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)
    
    def Underline(self) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<u>{self}</u>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)
    
    def Strikethrough(self) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<s>{self}</s>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)
    
    def Spoiler(self) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<tg-spoiler>{self}</tg-spoiler>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)
    
    def Link(self, href: str) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<a href="{href}">{self}</a>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)

    def LinkUsername(self, username: str) -> 'TextFormat':
        if len(username) > 0 and username[0] == '@':
            username = username[1:]
        return self.Link(f'https://t.me/{username}')
    
    def Pre(self) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<pre>{self}</pre>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)
    
    def Code(self, language: Union[Literal['python'], str]) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<code class="language-{language}">{self}</code>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)
    
    def Blockquote(self, expandable: bool = False) -> 'TextFormat':
        match self.parse_mode:
            case ParseMode.HTML:
                text = f'<blockquote {'expandable' if expandable else ''}>{self}</blockquote>'
            
            case _:
                raise RuntimeError()
        return TextFormat(text, parse_mode=self.parse_mode, screen_symbols=False)
            
    @property
    def parse_mode(self) -> ParseMode:
        return self._parse_mode
        
