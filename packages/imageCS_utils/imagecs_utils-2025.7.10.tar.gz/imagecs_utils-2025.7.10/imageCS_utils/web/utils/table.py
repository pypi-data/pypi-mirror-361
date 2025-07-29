"""generate html table string"""

from typing import List

_DEFAULT_TABLE_STYLE = """
<style>
h1 {text-align: center;}

table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}
th {
  border: 1px solid #000000;
  text-align: center;
  padding: 8px;
  background-color: #dddddd;
  color: #000000;
}
td {
  border: 1px solid #000000;
  text-align: center;
  padding: 8px;
  color: #000000;
}
</style>
"""

class TableHTML:
    """an easy table html generator"""
    def __init__(self, table_style:str=_DEFAULT_TABLE_STYLE, extra_style:str=""):
        self.__style:str = table_style + extra_style

        self.__title:str = "Table"
        self.__head:List[str]|None = None
        self.__num_col:int|None = None

        self.__rows_list:List[List[str]] = []
    
    def __assert_init(self):
        assert self.__head is not None, "make sure been set table head"
    
    def __assert_str(self, item_list):
        assert all(isinstance(item, str) for item in item_list), "make sure all item in list are string type"
    
    def set_title(self, title:str):
        self.__title = title
    
    def set_head(self, head:List[str]):
        """set table head"""
        self.__assert_str(head)
        self.__head = head
        self.__num_col = len(head)
    
    def append_row(self, row:List[str]):
        """append a table row"""
        self.__assert_init()
        assert len(row) == self.__num_col, "make sure the col num of row is same as head's col num"
        self.__assert_str(row)
        self.__rows_list.append(row)
    
    def _list2html(self, string_list:List[str], html_label:str):
        html_str = f"<{html_label}>" + f"</{html_label}><{html_label}>".join(string_list) + f"</{html_label}>"
        return html_str
    
    def _generate_head(self):
        self.__assert_init()
        html_head = "<tr>"
        html_end = "</tr>"
        html_context = self._list2html(self.__head, "th") # type: ignore

        html_str = html_head + html_context + html_end
        return html_str

    def _generate_rows(self):
        self.__assert_init()
        if len(self.__rows_list) == 0:
            return ""

        html_str = ""
        for row in self.__rows_list:
            context = self._list2html(row, "td")
            html_str = html_str + f"<tr>{context}</tr>"

        return html_str

    
    def generate_html(self):
        """generate html text"""
        table_style = self.__style
        table_head = self._generate_head()
        table_rows = self._generate_rows()

        html_str = table_style + f"<h1>{self.__title}</h1>" + f"<table>{table_head}\n{table_rows}</table>"
        return html_str
