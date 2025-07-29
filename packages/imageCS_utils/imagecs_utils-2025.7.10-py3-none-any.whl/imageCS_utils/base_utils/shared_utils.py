"""shared utils in base utils"""
import os
import shutil
import time
import subprocess as sp

from tqdm import tqdm
from functools import partialmethod

import torch
from .info import Info

def get_gpu_memory(gpu_num=None):
    """
    Get GPU used memory and total memory (util is MB)
    fork from https://stackoverflow.com/questions/67707828/how-to-get-every-seconds-gpu-usage-in-python
    @Vivasvan Patel
    """
    output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]
    split_memory = lambda memory_info: [int(x.split()[0]) for i, x in enumerate(memory_info)]
    command_used = "nvidia-smi --query-gpu=memory.used --format=csv"
    command_total = "nvidia-smi --query-gpu=memory.total --format=csv"
    try:
        memory_used_info = output_to_list(sp.check_output(command_used.split(),stderr=sp.STDOUT))[1:]
        memory_total_info = output_to_list(sp.check_output(command_total.split(),stderr=sp.STDOUT))[1:]
        memory_used_mb = split_memory(memory_used_info)
        memory_total_mb = split_memory(memory_total_info)
    except sp.CalledProcessError:
        memory_used_mb = [0]*1024
        memory_total_mb = [0]*1024
        Info.warn(f"Failed to run command:\n\t{command_used}\n\t{command_total}\nPlease check it.")

    if gpu_num is None:
        return (memory_used_mb, memory_total_mb)
    elif isinstance(gpu_num, int):
        memory_used_mb_ = memory_used_mb[gpu_num]
        memory_total_mb_ = memory_total_mb[gpu_num]
        return (memory_used_mb_, memory_total_mb_)
    elif isinstance(gpu_num, list):
        memory_used_mb_ = [memory_used_mb[i] for i in gpu_num]
        memory_total_mb_ = [memory_used_mb[i] for i in gpu_num]
        return (memory_used_mb_, memory_total_mb_)
    else:
        raise TypeError(f"Assert type(gpu_num) in (None, int, list), but get {type(gpu_num)}.")

class TimeStatistic:
    """easy way to statistic time, like tic and toc in MATLAB"""
    def __init__(self) -> None:
        self.start_flag = False
        self.data = []
        self.num = []
        self.tmp_start_time = None
    
    def start(self):
        """start timer (like tic in MATLAB)"""
        assert not self.start_flag
        self.start_flag = True
        self.tmp_start_time = time.time()
    
    def stop(self):
        """stop timer (like toc in MATLAB)"""
        assert self.start_flag
        now_time = time.time()

        delta_time = now_time - self.tmp_start_time
        self.data.append(delta_time)

        self.start_flag = False
    
    def step(self, step_num=1):
        """step timer (like toc in MATLAB)"""
        self.num.append(step_num)
    
    def clear(self):
        """clear all timer"""
        self.start_flag = False
        self.data = []
        self.num = []
        self.tmp_start_time = None

    def statistic(self, statistic_type="avg"):
        """get statistic"""
        assert statistic_type in ["avg", "sum"]

        sum_time = sum(self.data)
        sum_num = sum(self.num)

        if statistic_type == "avg":
            return_data = sum_time / sum_num
        elif statistic_type == "sum":
            return_data = sum_time
        else:
            raise TypeError()
        
        return return_data

def init_folder_path(*args, overwrite=False):
    """init a folder, is overwrite is True, the folder will be empty first"""
    for path in args:
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            if overwrite:
                shutil.rmtree(path)
                os.makedirs(path)

def get_optimizer_lr(optimizer:torch.optim.Optimizer):
    """get the optimizer learning rate"""
    for param_group in optimizer.param_groups:
        return param_group['lr']

def argv2str(argv_list:list):
    """argv to str"""
    s = ""
    for arg in argv_list:
        s += arg + " "
    return s[:-1]

########################## Dict Update ##########################
class DictUpdate:
    @staticmethod
    def replace(operated_dict:dict, value, *keys):
        """Replace the value of the operated_dict while make sure all keys have been in the operated_dict


        Args:
            operated_dict (dict): The dict be operated
            value: The value to be updated
            keys: Recursive keys in Dict to be updated

        Example:
            The fuction of ```DictUpdate.replace(d, 24, "a", "b", "c")``` means d["a"]["b"]["c"] = 24,
            while make sure that d["a"]["b"]["c"] has been exist.

        Raises:
            ValueError: the keys must have at least 1 argument
        """
        assert type(operated_dict) is dict, "The operated_dict or the sub-dict of operated_dict is not a dict"
        match len(keys):
            case 0:
                raise ValueError("keys expected at least 1 argument")
            case 1:
                k = keys[-1]
                assert k in operated_dict, f"The key <{k}> is not in the dict"
                operated_dict[k] = value
            case _:
                k = keys[0]
                assert k in operated_dict, f"The key <{k}> is not in the dict"
                DictUpdate.replace(operated_dict[k], value, *keys[1:])

    @staticmethod
    def insert(operated_dict:dict, value, *keys):
        """Insert the value of the operated_dict while make sure all keys expect the last have been in the operated_dict,
        and make sure the last key has NOT been exist


        Args:
            operated_dict (dict): The dict be operated
            value: The value to be insert
            keys: Recursive keys in Dict to be updated

        Example:
            The fuction of ```DictUpdate.insert(d, 24, "a", "b", "c")``` means d["a"]["b"]["c"] = 24,
            while make sure that d["a"]["b"] has been exist and d["a"]["b"]["c"] has NOT been exist.

        Raises:
            ValueError: the keys must have at least 1 argument
        """
        assert type(operated_dict) is dict, "The operated_dict or the sub-dict of operated_dict is not a dict"
        match len(keys):
            case 0:
                raise ValueError("keys expected at least 1 argument")
            case 1:
                k = keys[-1]
                assert not (k in operated_dict), f"The key <{k}> has been exist in the dict"
                operated_dict[k] = value
            case _:
                k = keys[0]
                assert k in operated_dict, f"The key <{k}> is not in the dict"
                DictUpdate.insert(operated_dict[k], value, *keys[1:])


def tensor_detach_and_cpu(data):
    """
    Conver all Tensor detached and to cpu in data:Any.
    """
    if isinstance(data, torch.Tensor):
        return data.detach().cpu()
    elif isinstance(data, dict):
        now_dict = {}
        for key, value in data.items():
            now_dict[key] = tensor_detach_and_cpu(value)
        return now_dict
    elif isinstance(data, list):
        now_list = []
        for d in data:
            now_list.append(tensor_detach_and_cpu(d))
        return now_list
    else:
        return data

class Disable_Tqdm:
    def __init__(self):
        pass
    
    def __enter__(self):
        Disable_Tqdm.disable_eqdm()
    
    def __exit__(self):
        Disable_Tqdm.enable_eqdm()
    
    @staticmethod
    def disable_eqdm():
        tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

    @staticmethod
    def enable_eqdm():
        tqdm.__init__ = partialmethod(tqdm.__init__, disable=False)

def get_iter_params(total_iter_num:int, total_epoch:int, batch_size:int):
    """ get iter_num_per_epoch and datset_len_per_epoch """
    iter_num_per_epoch = total_iter_num / total_epoch
    dataset_len_per_epoch = iter_num_per_epoch * batch_size

    iter_num_per_epoch = round(iter_num_per_epoch)
    dataset_len_per_epoch = round(dataset_len_per_epoch)

    return (iter_num_per_epoch, dataset_len_per_epoch)
