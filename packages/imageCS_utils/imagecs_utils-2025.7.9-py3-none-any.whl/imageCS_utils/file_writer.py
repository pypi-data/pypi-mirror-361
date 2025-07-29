import os
from .utils import init_folder_path
import datetime

class Text_Writer:
    def __init__(self, folder, file_name):
        init_folder_path(folder)
        self.path = os.path.join(folder, file_name)
    
    def write(self, text, mode="a"):
        with open(self.path, mode, encoding='utf-8') as f:
            f.write(text)

class Log_Writer(Text_Writer):
    def write(self, one_line_info):
        timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        super().write(f"[{timestr}] {one_line_info}\n")