import re
import shutil
from dataclasses import dataclass

from re import Match as MatchClass
from glob import glob

import torch.nn as nn
import torch

from utils.base_utils.info import Info
from utils.utils import init_folder_path, load_single_image, save_single_image

@dataclass
class __PSNR_SSIM_Info:
    name:str
    psnr:float
    ssim:float
    x_true_path:str
    x_pred_path:str

def get_difference_from_max_value(target_value:int|float, compares_value:list[int|float]):
    return target_value - max(compares_value)

def sort_difference_from_max_value(target_values:list[int|float], compares_values:list[list[int|float]]) -> list[int]:
    """
    get sorted index (from max to min)
    """
    differences:list[int|float] = []
    for (target_value, compares_value) in zip(target_values, compares_values):
        differences.append(get_difference_from_max_value(target_value, compares_value))
    (_, argmins) = torch.tensor(differences).sort()
    argmins = argmins.tolist()
    argmaxs = argmins[::-1]
    return argmaxs

def get_match_ans(match_ans:MatchClass[str]|None) -> str|None:
    if match_ans is not None:
        match_ans = match_ans.group(1) # type: ignore
    else:
        match_ans = None
    return match_ans # type: ignore

def get_metrics_filename(folder_path:str, match_str:str):
    if folder_path[-1] == "/":
        folder_path = folder_path[:-1]
        
    match_path = glob(f"{folder_path}/{match_str}")
    assert len(match_path) == 1, f"error on glob {folder_path}/{match_str}"
    match_path = match_path[0]
    match_filename = match_path[len(folder_path)+1:]
    return match_filename


def _match_psnr(file_name:str) -> float:
    match_ans = re.match(r"PSNR-(.*).png", file_name)
    match_ans = get_match_ans(match_ans)
    assert match_ans is not None
    psnr = float(match_ans)
    
    return psnr

def _match_ssim(file_name:str) -> float:
    match_ans = re.match(r"SSIM-(.*).png", file_name)
    match_ans = get_match_ans(match_ans)
    assert match_ans is not None
    ssim = float(match_ans)

    return ssim
    
def match_psnr(folder_path:str):
    """
    return  psnr:float
    """
    psnr = _match_psnr(get_metrics_filename(
        folder_path = folder_path,
        match_str = "PSNR-*.png"
    ))
    return psnr

def match_ssim(folder_path:str):
    """
    return  ssim:float
    """
    ssim = _match_ssim(get_metrics_filename(
        folder_path = folder_path,
        match_str = "SSIM-*.png"
    ))

    return ssim

def generate(target_folder:str, compares_folder:list[str], target_name:str, compares_name:list[str]):
    target_info = __PSNR_SSIM_Info(
        name = target_name,
        psnr = match_psnr(target_folder),
        ssim = match_ssim(target_folder),
        x_true_path = f"{target_folder}/x_true.png",
        x_pred_path = f"{target_folder}/x_pred.png",
    )

    compares_info = [__PSNR_SSIM_Info(
        name = compare_name,
        psnr = match_psnr(compare_folder),
        ssim = match_ssim(compare_folder),
        x_true_path = f"{compare_folder}/x_true.png",
        x_pred_path = f"{compare_folder}/x_pred.png",
    ) for compare_folder, compare_name in zip(compares_folder, compares_name)]

    return (target_info, compares_info)

def sort_all(target_infos:list[__PSNR_SSIM_Info], compares_infos: list[list[__PSNR_SSIM_Info]]):
    """
    return sorted_index (from max to min)
    """
    sorted_indexs = sort_difference_from_max_value(
            target_values = [target_info.psnr for target_info in target_infos],
            compares_values = [[compare_info.psnr for compare_info in compares_info] for compares_info in compares_infos]
    )
    return sorted_indexs

def generate_all(taregt_folders:list[str], compares_folders:list[list[str]], target_name:str, compares_name:list[str]):
    """
    info = class{name, psnr, ssim, x_true_path, x_pred_path}
    return [
        [compare1_info1, ..., comapareX_info1],
        [compare1_info2, ..., comapareX_info2],
        ...,
        [compare1_infoN, ..., comapareX_infoN],
    ]

    """
    target_infos:list[__PSNR_SSIM_Info] = []
    compares_infos:list[list[__PSNR_SSIM_Info]] = []
    for target_folder, compares_folder in zip(taregt_folders, compares_folders):
        (target_info, compares_info) = generate(target_folder, compares_folder, target_name, compares_name)
        target_infos.append(target_info)
        compares_infos.append(compares_info)

    return target_infos, compares_infos

def match_info_all(target_infos:list[__PSNR_SSIM_Info], compares_infos:list[list[__PSNR_SSIM_Info]]):
    """
    match the all info
    such as the compare1_info1 may match target_info6 instead of target_info1
    return the matched targets_info and compares_infos
    """
    matched_compares_infos:list[list[__PSNR_SSIM_Info]] = [compares_info.copy() for compares_info in compares_infos]

    number_infos = len(compares_infos)
    number_compares = len(compares_infos[0])

    for ptr_compare in range(number_compares):
        for ptr_info_target in range(number_infos):
            Info.info(f"                                         ", end="\r")
            Info.info(f"Matching ({ptr_compare+1}/{number_compares})({ptr_info_target+1}/{number_infos})", end="\r")
            err_tensor = torch.empty((number_infos, ), dtype=torch.float32).view(-1)
            target_true_image = load_single_image(target_infos[ptr_info_target].x_true_path)
            for ptr_info_compare in range(number_infos):
                compare_true_image = load_single_image(compares_infos[ptr_info_compare][ptr_compare].x_true_path)

                if target_true_image.size() == compare_true_image.size():
                    err = (target_true_image - compare_true_image).pow(2).mean().item()
                else:
                    err = float("+inf")
                
                err_tensor[ptr_info_compare] = err

            # put comapres infos to true position to match target
            true_ptr = int(err_tensor.argmin().item())
            matched_compares_infos[ptr_info_target][ptr_compare] = compares_infos[true_ptr][ptr_compare]
    print()
        
    return matched_compares_infos

def copy_file(info:__PSNR_SSIM_Info, save_folder:str, copy_x_true=False):
    shutil.copyfile(
        info.x_pred_path,
        f"{save_folder}/{info.name}_PSNR-{info.psnr:.2f}_SSIM-{info.ssim:.4f}.png"
    )

    if copy_x_true:
        shutil.copyfile(
            info.x_true_path,
            f"{save_folder}/x_true.png"
        )

def save_from_max_to_min(save_root:str, target_infos:list[__PSNR_SSIM_Info], compares_infos:list[list[__PSNR_SSIM_Info]], sorted_indexs:list[int]):
    for i, sorted_idx in enumerate(sorted_indexs):
        target_info = target_infos[sorted_idx]
        compare_infos = compares_infos[sorted_idx]

        save_folder = f"{save_root}/{i}"
        init_folder_path(save_folder)
        copy_file(target_info, save_folder, copy_x_true=True)
        for compare_info in compare_infos:
            copy_file(compare_info, save_folder)

def psnr_compare_save(save_root:str, taregt_folders:list[str], compares_folders:list[list[str]], target_name:str, compares_name:list[str], auto_match=True):
    """Compare the comparison target with compared targets, then save them to the save_root

    Args:
        save_root (str):
            the folder path used to save compared images (from max to min)

        taregts_folder (list[str]):
            The folder path list of comparison target,
            such as ["main/image/1", "main/image/2", ..., "main/image/n"]

        compares_folders (list[list[str]]):
            The list of folder path list of compared targets,
            such as [
                ["compare_A/image/1", "compare_B/image/1", ..., "compare_Z/image/1"],
                ["compare_A/image/2", "compare_B/image/2", ..., "compare_Z/image/2"],
                ...,
                ["compare_A/image/n", "compare_B/image/n", ..., "compare_Z/image/n"],
            ]

        target_name (str):
            The name of comparison target, such as "main"

        compares_name (list[str]):
            The name list of compared target, such as ["compare_A", "compare_B", ..., "compare_N"]
    
    The folder tree of comparison target folder or compared target folder, such as:
    main/image/1
    ├── PSNR-27.28.png
    ├── SSIM-0.8576.png
    ├── x_pred.png
    └── x_true.png
    """
    Info.info("[step 1/3] Generating...")
    (target_infos, compares_infos) = generate_all(taregt_folders, compares_folders, target_name, compares_name)
    Info.info("[step 2/3] Generated, Matching...")
    if auto_match:
        compares_infos = match_info_all(target_infos, compares_infos)
    Info.info("[step 3/3] Matched, Saving...")
    sorted_indexs = sort_all(target_infos, compares_infos)
    save_from_max_to_min(save_root, target_infos, compares_infos, sorted_indexs)
