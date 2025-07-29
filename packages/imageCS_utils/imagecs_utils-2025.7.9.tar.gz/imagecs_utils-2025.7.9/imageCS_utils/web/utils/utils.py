"""some html and web utils"""
from typing import Dict

class TextStyle:
    """get text style html"""
    def __init__(self, text:str|None=None, default_style_dict:Dict[str, str]|None=None):
        self.__text = text
        self.__style_dict = {} if default_style_dict is None else default_style_dict
    
    def set_color(self, color:str):
        """set text color, for example: #0000ff"""
        self.__style_dict["color"] = color
    
    def set_background_color(self, color:str):
        """set text color, for example: #0000ff"""
        self.__style_dict["background-color"] = color
    
    def set_font_family(self, font:str):
        """set text font family, for example: arial"""
        self.__style_dict["font-family"] = font
    
    def set_font_size(self, font_size:str):
        """set text font size, for example: 14px"""
        self.__style_dict["font-size"] = font_size
    
    def set_others(self, style_name:str, style_item:str):
        """set other text style, i.e. {style_name}: {style_item};"""
        self.__style_dict[style_name] = style_item
    
    def generate_html(self):
        """generate html text"""
        assert self.__text is not None
        styles = [f"{style_type}: {style_item}" for (style_type, style_item) in self.__style_dict.items()]
        styles = ";".join(styles)
        html_text = f'<span style="{styles}">{self.__text}</span>'

        return html_text
    
    def get_style_dict(self):
        """return a copy of self.__style_dict"""
        return self.__style_dict.copy()

class TextStyleGenerator:
    """generate text with same style"""
    def __init__(self, text_style:TextStyle):
        self.__text_style_dict = text_style.get_style_dict()
    
    def generate_html(self, text:str):
        """generate html text"""
        text_style = TextStyle(text=text, default_style_dict=self.__text_style_dict)
        return text_style.generate_html()
    
    def __call__(self, text:str):
        """generate html text"""
        return self.generate_html(text)
