"""Auto hold all GPU memory"""
from threading import Thread
from multiprocessing import Process, Manager
import time
import os

import torch
from torch.autograd import Variable

from .shared_utils import get_gpu_memory

def mb_to_b(x):
    """convert MB to B"""
    return x * 1024 * 1024

class GPUHolder():
    """auto hold all GPU memory"""
    def __init__(self, reverse_size=512, sleep_time=120, gpu_num:int|list[int]|None=None, force_mode=False, reflesh_time=60*10, using_process=False):
        """
        reverse_size (MB)
        sleep_time (s)
        """
        assert gpu_num is None or type(gpu_num) in [int, list]
        if isinstance(gpu_num, int):
            gpu_num = [gpu_num]

        self.reverse_mem = mb_to_b(reverse_size)

        self.manager = Manager()
        self.shared_dict = self.manager.dict()
        self.using_process = using_process

        self.shared_dict["alloc_mem_flag"] = False
        self.shared_dict["reflesh_mem_flag"] = False
        self.shared_dict["holding_mem_flag"] = False

        self.sleep_time=sleep_time
        self.reflesh_time = reflesh_time

        self.proc = Process()

        if gpu_num is not None:
            self._set_device(gpu_num)
        
        self.force_mode = force_mode

        self.virtual_gpu_num_list = [d for d in range(torch.cuda.device_count())]

        
        if gpu_num is None:
            self.real_gpu_num_list = self.virtual_gpu_num_list
        else:
            self.real_gpu_num_list = sorted(gpu_num)

    def _set_device(self, gpu_num:list[int]):
        assert isinstance(gpu_num, list)
        set_str = ",".join([str(g) for g in gpu_num])
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"] = set_str
    
    def start(self):
        """start hold gpu memory"""
        self.shared_dict["alloc_mem_flag"] = True
        if self.using_process:
            self.proc = Process(
                target=self._hold,
                args=(self.shared_dict,),
                daemon=True
            )
        else:
            self.proc = Thread(
                target=self._hold,
                args=(self.shared_dict,),
                daemon=True
            )
        self.proc.start()

    def stop(self):
        """stop hold gpu memory"""
        self.shared_dict["alloc_mem_flag"] = False

        while self.shared_dict["holding_mem_flag"]:
            time.sleep(1)
        time.sleep(1)

    def _reflesh_obj(self, shared_dict, tmp_list):
        while shared_dict["alloc_mem_flag"]:
            self._reflesh_all_obj(tmp_list)
            time.sleep(self.reflesh_time)
    
    def _reflesh_all_obj(self, tmp_list):
        l = len(tmp_list)
        for i in range(l):
            tmp_list[i][:] += 1

    def _get_empty_uint8(self, alloc_mem, dev):
        size = alloc_mem
        data = torch.zeros((size,), dtype=torch.uint8, device=dev, requires_grad=False)
        return data
    
    def _hold_memory(self, virtual_gpu_num, tmp_list):
        dev = torch.device(f"cuda:{virtual_gpu_num}")
        real_gpu_num = self.real_gpu_num_list[virtual_gpu_num]
        hold_mem = self._get_empty_uint8(64, dev)
        tmp_list.append(hold_mem)

        def get_alloc_mem():
            (used_mem, total_mem) = get_gpu_memory(real_gpu_num)
            total_mem = mb_to_b(total_mem)
            used_mem = mb_to_b(used_mem)
            free_mem = total_mem - used_mem
            alloc_mem = free_mem - self.reverse_mem

            return alloc_mem

        alloc_mem = get_alloc_mem()
        if alloc_mem > 0:
            while True:
                delta_mem = alloc_mem - self.reverse_mem
                if delta_mem > 0:
                    hold_object = self._get_empty_uint8(self.reverse_mem, dev)
                    tmp_list.append(hold_object)
                    alloc_mem = get_alloc_mem()
                else:
                    if alloc_mem > 0:
                        try:
                            hold_object = self._get_empty_uint8(alloc_mem, dev)
                            tmp_list.append(hold_object)
                        except RuntimeError:
                            pass
                    break
    
    def _hold_memory_force(self, virtual_gpu_num, tmp_list):
        dev = torch.device(f"cuda:{virtual_gpu_num}")
        alloc_mem = self.reverse_mem
        try:
            while True:
                hold_object = self._get_empty_uint8(alloc_mem, dev)
                tmp_list.append(hold_object)
        except RuntimeError:
            pass
        
    def _hold_all(self, shared_dict, tmp_list):
        if shared_dict["alloc_mem_flag"]:
            for virtual_gpu_num in self.virtual_gpu_num_list:
                if self.force_mode:
                    self._hold_memory_force(virtual_gpu_num, tmp_list)
                else:
                    self._hold_memory(virtual_gpu_num, tmp_list)
    
    def _hold(self, shared_dict):
        self.shared_dict["holding_mem_flag"] = True
        time.sleep(self.sleep_time)
        tmp_list = []
        self._hold_all(shared_dict, tmp_list)

        thread_reflesh = Thread(
            target=self._reflesh_obj,
            args=(shared_dict, tmp_list, ),
            daemon=True
        )
        thread_reflesh.start()

        while shared_dict["alloc_mem_flag"]:
            time.sleep(1)
        
        # empty the tmp variable in gpu mem.
        # tips: directly delete tmp_list cannot release the variable in gpu mem
        # so I pop the Tensor from list and covert it with Variable(), and then delete it
        while tmp_list:
            tmp_data = tmp_list.pop()
            tmp_data = Variable(tmp_data)
            del tmp_data
        self.shared_dict["holding_mem_flag"] = False
        
