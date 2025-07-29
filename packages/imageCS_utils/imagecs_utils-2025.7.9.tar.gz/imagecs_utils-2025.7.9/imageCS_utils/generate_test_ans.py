"""generate the testset metrics ans"""
#pylint: disable=consider-using-f-string
import re
from glob import glob
from typing import Any, Callable, List

import torch
from torch import Tensor

from .base_utils.info import Info
from .web.utils.utils import TextStyle, TextStyleGenerator
from .web.simple_web import start_simple_web
from .web.utils.table import TableHTML

def generate_any_thing(folder_path:str, str_before_value:str, str_after_value:str, typing_value_func=float) -> Any|None:
    """
    generate any things from folder path
    e.g. exist folder_path/PSNR-36.05.png
    set str_before_value="PSNR-", str_after_value=".png"
    return 36.05

    if there is not exist folder_path/PSNR-*.png
    return None
    """
    glob_str = f"{folder_path}/{str_before_value}*{str_after_value}"
    match_str = r"{}/{}(.*){}".format(folder_path, str_before_value, str_after_value)

    match_files = glob(glob_str)
    if len(match_files) == 0:
        return None
    
    file_name = match_files[0]
    if len(match_files) > 1:
        Info.warn(f"More than 1 matched file name in '{glob_str}', only use '{file_name}' to match.")

    match_value = re.match(match_str, file_name)
    if match_value is not None:
        value = match_value.group(1)
        value = typing_value_func(value)
        return value

    return None

def generate_psnr(folder_path:str) -> float|None:
    """e.g. exist folder_path/PSNR-36.05.png and return 36.05"""
    return generate_any_thing(
        folder_path=folder_path,
        str_before_value="PSNR-",
        str_after_value=".png"
    )

def generate_ssim(folder_path:str) -> float|None:
    """e.g. exist folder_path/SSIM-0.9864.png and return 0.9864"""
    return generate_any_thing(
        folder_path=folder_path,
        str_before_value="SSIM-",
        str_after_value=".png"
    )

def generate_fid(folder_path:str) -> float|None:
    """e.g. exist folder_path/FID-21.98.png and return 21.98"""
    return generate_any_thing(
        folder_path=folder_path,
        str_before_value="FID-",
        str_after_value=".png"
    )

def generate_lpips(folder_path:str) -> float|None:
    """e.g. exist folder_path/LPIPS-0.2135.png and return 0.2135"""
    return generate_any_thing(
        folder_path=folder_path,
        str_before_value="LPIPS-",
        str_after_value=".png"
    )

def read_value(folder_path_table:List[List[str]], generate_func:Callable[..., int|float|None], **func_kwargs) -> List[List[int|float|None]]:
    """read value via 2D folder path table, return table where the value is at the corresponding position"""
    value_table:List[List[int|float|None]] = []

    for row in folder_path_table:
        value_row:List[int|float|None] = []
        for folder_path in row:
            value_row.append(generate_func(folder_path, **func_kwargs))
        value_table.append(value_row)
    return value_table

def set_value_table_color(value_table:Tensor|List[List[Any]], sort_method:str, sort_scope:str, rank_color:List[str], fmt_way="{}"):
    """ get html colored value via min or max sort

    Args:
        value_table (Tensor | List[List[Any]]): value table
        sort_method (str): "min" or ""max
        sort_pos (str): "row" or "col"
        rank_color (List[str]): e.g. rank_color=["#00ff00", "ff0000"], and the rank1 value use rank_color[0] and so on.
        fmt_way (str): format value to string using fmt.way.format(value)
    """
    assert sort_method in ["min", "max"]
    assert sort_scope in ["row", "col"]
    assert isinstance(value_table, (List, Tensor))

    if isinstance(value_table, List):
        Info.warn("We recommand use Tensor type for value_table instead of List")
        value_table = torch.tensor(value_table)
    
    # sort from small to big
    sort_arg = value_table.argsort(dim=1) if sort_scope == "row" else value_table.argsort(dim=0)
    assert len(rank_color) - 1 <= sort_arg.max()

    value_table = value_table.tolist()
    value_table = [[fmt_way.format(value) for value in row] for row in value_table]

    text_style = TextStyle()
    for (rank, color) in enumerate(rank_color):
        text_style.set_color(color)
        text_style_gen = TextStyleGenerator(text_style)
        if sort_scope == "row":
            if sort_method == "min":
                for h, pos in enumerate(sort_arg[:, rank]):
                    value_table[h][pos] = text_style_gen(value_table[h][pos])
            else:
                for h, pos in enumerate(sort_arg[:, -(rank+1)]):
                    value_table[h][pos] = text_style_gen(value_table[h][pos])
        else:
            if sort_method == "min":
                for w, pos in enumerate(sort_arg[rank, :]):
                    value_table[pos][w] = text_style_gen(value_table[pos][w])
            else:
                for w, pos in enumerate(sort_arg[-(rank+1), :]):
                    value_table[pos][w] = text_style_gen(value_table[pos][w])
    
    return value_table

class DifferentDatasetTable:
    def _get_path_list(self, save_path:str, dataset_names:list[str]):
        """get"""
        path_row = [f"{save_path}/test/{dataset_name}" for dataset_name in dataset_names]
        return path_row

    def _get_path_table(self, save_paths:list[str], dataset_names:list[str]):
        """doc"""
        table = [self._get_path_list(save_path, dataset_names) for save_path in save_paths]
        return table
    
    def show_table_via_web(self, save_paths_dict:dict[str, str], dataset_names:list[str], cs_ratio:str|float, port:int):
        """
        main function for showing table
        save_paths_dict: dict[name:str, save_path:str]
        """

        name_list = list(save_paths_dict.keys())
        save_paths = list(save_paths_dict.values())

        path_table = self._get_path_table(save_paths, dataset_names)

        psnr_table = read_value(path_table, generate_psnr)
        psnr_table = set_value_table_color(psnr_table, "max", "col", ["#ff0000", "#0000ff"], fmt_way="{0:.2f}")

        ssim_table = read_value(path_table, generate_ssim)
        ssim_table = set_value_table_color(ssim_table, "max", "col", ["#ff0000", "#0000ff"], fmt_way="{0:.4f}")

        fid_table = read_value(path_table, generate_fid)
        fid_table = set_value_table_color(fid_table, "min", "col", ["#ff0000", "#0000ff"], fmt_way="{0:.2f}")

        lpips_table = read_value(path_table, generate_lpips)
        lpips_table = set_value_table_color(lpips_table, "min", "col", ["#ff0000", "#0000ff"], fmt_way="{0:.4f}")

        table_html = TableHTML()

        table_html.set_title(f"PSNR/SSIM/FID/LPIPS under CS ratio = {cs_ratio}")
        table_html.set_head(["Method"] + dataset_names)
        for ver_name, psnr_row, ssim_row, fid_row, lpips_row in zip(name_list, psnr_table, ssim_table, fid_table, lpips_table):
            table_html.append_row([ver_name] + [f"{psnr}/{ssim}/{fid}/{lpips}" for (psnr, ssim, fid, lpips) in zip(psnr_row, ssim_row, fid_row, lpips_row)])
        table_html = table_html.generate_html()

        start_simple_web(
            context=table_html,
            port=port
        )
