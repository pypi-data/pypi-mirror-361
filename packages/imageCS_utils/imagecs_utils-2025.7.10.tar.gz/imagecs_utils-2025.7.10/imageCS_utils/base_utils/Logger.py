"""Logger: Auto save and load training process"""
# pylint: disable=invalid-name, broad-exception-caught
import pickle
import csv
import glob
import os

import threading
from threading import Lock
from datetime import datetime
from time import sleep

import numpy as np
import torch
from torch.nn import Module
from torch.optim.lr_scheduler import LRScheduler
from torch.optim import Optimizer

from matplotlib import pyplot as plt
from .info import Info

def get_newest_timestamp(kernel_folder:str):
    """
    Get newest kernel via timestamp in the kernel folder

    Return the newest timestamp if find the kernel file
    Else return -1
    """
    net_file_path_list = glob.glob(f"{kernel_folder}/kernel_*.pkl")
    max_timestamp = -1
    for net_file_path in net_file_path_list:
        file_timestamp = int(net_file_path[-18: -4])
        if file_timestamp > max_timestamp:
            max_timestamp = file_timestamp
    
    return max_timestamp

def get_state_dict(logger_folder:str, timestamp:int|None=None, dev:str|torch.device="cpu", weight_only=True):
    if timestamp == None:
        timestamp = get_newest_timestamp(logger_folder)
    kernel_path = f"{logger_folder}/kernel_{timestamp}.pkl"
    kernel = Logger_Kernel.load(kernel_path)
    net_path = f"{logger_folder}/{kernel.logfile_info['net']}"
    state_dict = torch.load(net_path, map_location=dev, weights_only=weight_only)
    return state_dict

class Logger_Kernel:
    """logger kernel: save all training processing data file path"""
    #def __init__(self, name="", logfile_info={}, extra_info={}, kernel_history=[]):
    def __init__(self, name="", logfile_info=None, extra_info=None, kernel_history=None):
        self.name = name
        self.logfile_info = {} if logfile_info is None else logfile_info
        self.extra_info = {} if extra_info is None else extra_info
        self.kernel_history = [] if kernel_history is None else kernel_history
    
    def update_base_info(self, name):
        """update name"""
        self.name = name
    
    def update_logfile_info(self, **logfile_info):
        """update logfile path"""
        self.logfile_info.update(logfile_info)
    
    def update_extra_info(self, **extra_info):
        """update other info"""
        self.extra_info.update(extra_info)
    
    def update_history(self, timestamp):
        """append history kernel"""
        self.kernel_history.append(timestamp)
    
    @staticmethod
    def load(filename):
        """load pkl file"""
        with open(filename, 'rb') as f:
            data:dict = pickle.load(file=f)
        
        if isinstance(data, dict):
            name:str = data["name"]
            logfile_info:dict = data["logfile_info"]
            extra_info:dict = data["extra_info"]
            kernel_history:list = data["kernel_history"]

            logger_kernel = Logger_Kernel(
                name = name,
                logfile_info = logfile_info,
                extra_info = extra_info,
                kernel_history = kernel_history
            )
        else:
            # old-type logger kernel file
            Info.warn("You're using old-type logger kernel file")
            logger_kernel = data

        return logger_kernel

    @staticmethod
    def save(kernel_logger, filename):
        """save kernel logger to pkl file"""
        name:str = kernel_logger.name
        logfile_info:dict = kernel_logger.logfile_info
        extra_info:dict = kernel_logger.extra_info
        kernel_history:list = kernel_logger.kernel_history

        data = dict(
            name = name,
            logfile_info = logfile_info,
            extra_info = extra_info,
            kernel_history = kernel_history
        )
        with open(filename, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    
class CSVOperator():
    """CSV Operator"""
    def __init__(self) -> None:
        self.buffer = []
        self.head_list = None
    
    def add(self, data:list[str|int|float]):
        """
        add data to buffer, example: ["Tom", 12, 65.9]
        """
        self.buffer.append(data)
    
    def clear(self):
        """clear buffer"""
        self.buffer = []

    def set_head(self, head_list:list[str], focus=False):
        """
        set csv head, example: ["Name", "Age", "Weight"]
        """
        if focus or self.head_list is None:
            self.head_list = head_list
    
    def save(self, file_path, clear_buffer=True):
        """append data to file from buffer, default clear buffer after writing"""
        with open(file_path, "a", newline='', encoding="utf-8") as f:
            csv_writter = csv.writer(f)
            if self.head_list is not None:
                csv_writter.writerow(self.head_list)
                if len(self.buffer) > 0:
                    csv_writter.writerows(self.buffer)
        
        if clear_buffer:
            self.clear()

    def override_save(self, file_path, clear_buffer=True):
        """override data and write data to file from buffer, default clear buffer after writing"""
        with open(file_path, "w", newline='', encoding='utf-8') as f:
            csv_writter = csv.writer(f)
            if self.head_list is not None:
                csv_writter.writerow(self.head_list)
                if len(self.buffer) > 0:
                    csv_writter.writerows(self.buffer)
        
        if clear_buffer:
            self.clear()
    
    def read(self, file_path):
        """read data from csv file"""
        with open(file_path, "r", newline='', encoding="utf-8") as f:
            csv_reader = csv.reader(f)
            l = list(csv_reader)
            if len(l) > 0:
                name = l[0]
            else:
                name = None
            if len(l) > 1:
                data = l[1:]
            else:
                data = None
        return (name, data)

class NetStorager():
    """save and load model state dict"""
    def __init__(self) -> None:
        pass

    def save(self, net, file_path):
        """save model state dict"""
        torch.save(net.state_dict(), file_path)
    
    def load(self, net, file_path, dev="cpu"):
        """load model state dict"""
        state_dict = torch.load(file_path, map_location=dev, weights_only=True)
        try:
            net.load_state_dict(state_dict)
        except Exception as E:
            Info.WARN(f"Load Net Fails:\n{E}")
            Info.warn("Now Trying Load Net Use Unstrict Mode")
            net.load_state_dict(state_dict, strict=False)

class OptimStorager():
    """save and load optimizer state dict"""
    def __init__(self) -> None:
        pass

    def save(self, optim, file_path):
        """save optimizer state dict"""
        torch.save(optim.state_dict(), file_path)
    
    def load(self, optim, file_path, dev="cpu"):
        """load optimizer state dict"""
        try:
            state_dict = torch.load(file_path, map_location=dev, weights_only=True)
            optim.load_state_dict(state_dict)
        except Exception as e:
            Info.WARN(f"Fail to load the state dict of optimizer: {str(e)}")

class LrSchedulerStorager():
    """save and load learning rate scheduler"""
    def __init__(self) -> None:
        pass

    def save(self, lr_scheduler_list, file_path):
        """save learning rate scheduler"""
        state_dict_list = []
        for lr_scheduler in lr_scheduler_list:
            state_dict_list.append(lr_scheduler.state_dict())
        torch.save(state_dict_list, file_path)
    
    def load(self, lr_scheduler_list, file_path, dev="cpu"):
        """load learning rate scheduler"""
        try:
            state_dict_list = torch.load(file_path, map_location=dev, weights_only=False)
            for lr_scheduler, state_dict in zip(lr_scheduler_list, state_dict_list):
                lr_scheduler.load_state_dict(state_dict)
        except Exception as e:
            Info.WARN(f"Fail to load the state dict of learning rate scheduler: {str(e)}")

class Logger:
    """auto load logger kernel and data via timestamp, if timestamp is None, create new logger kernel"""
    def __init__(self, dir_path:str,
                 net:torch.nn.Module, optim:Optimizer|None=None, lr_scheduler_list:list[LRScheduler]|None=None,
                 timestamp:int|None=None, load_newest=False, rollback_epoch=None, thread_save=False):
        '''
        If timestamp is not, create new logger kernel, else load kernel and data
        '''

        assert not (timestamp is not None and load_newest)

        self.train_logger = CSVOperator()
        self.eval_logger = CSVOperator()
        self.plot_logger = CSVOperator()
        self.net_storager = NetStorager()
        self.optim_storager = OptimStorager()
        self.lr_scheduler_storager = LrSchedulerStorager()

        self.dir_path = dir_path
        self.thread_save = thread_save

        self.net = net
        self.optim = optim
        self.lr_scheduler_list = lr_scheduler_list
        self.kernel = Logger_Kernel()

        self.lock = Lock()
        self.using_temp_kernel = False

        # Load Kernel
        self.auto_load_kernel(timestamp, load_newest)
        
        # Rollback Epoch
        if rollback_epoch is not None:
            self.rollback(epoch=rollback_epoch)
    
    def auto_load_kernel(self, timestamp, load_newest, dir_path:str|None = None):
        """auto load kernel"""
        dir_path = self.dir_path if dir_path is None else dir_path

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        kernel_path = f"{dir_path}/kernel_{timestamp}.pkl"
        if timestamp is not None and os.path.exists(kernel_path):
            self.load_kernel(timestamp, dir_path)
            Info.info(f'Loaded kernel, timestamp: {timestamp}')
            self.print_info()
        elif load_newest:
            max_timestamp = get_newest_timestamp(dir_path)
            if max_timestamp >= 0:
                self.load_kernel(max_timestamp, dir_path)
                Info.info(f'Loaded kernel, timestamp: {max_timestamp}')
                self.print_info()
            else:
                Info.warn("Cannot find any kernel, create a new logger kernel")
                self.new_kernel()
        else:
            self.new_kernel()
            Info.info("Create a new logger kernel")

        if "temp_kernel" in self.kernel.extra_info and self.kernel.extra_info["temp_kernel"] is True:
            Info.info('Loaded temp kernel')
            self.using_temp_kernel = True
            temp_kernel_tiimestamp = self.kernel.extra_info["temp_kernel_timestamp"]
            self._load_train_and_eval(temp_kernel_tiimestamp)
        else:
            self.using_temp_kernel = False
    
    def rollback(self, epoch, dir_path:str|None=None):
        """roll back training process via epoch"""
        dir_path = self.dir_path if dir_path is None else dir_path
        kernel = self.kernel
        timestamp_history = kernel.kernel_history

        for timestamp in reversed(timestamp_history):
            kernel_path = f"{dir_path}/kernel_{timestamp}.pkl"
            kernel = Logger_Kernel.load(kernel_path)
            history_epoch = kernel.extra_info["epoch"]

            if history_epoch == epoch:
                self.load_kernel(timestamp, dir_path)
                Info.info(f"Rollback to {epoch} epoch")
                self.print_info()
                break
            elif history_epoch < epoch:
                Info.WARN(f"Not find {epoch} epoch in history kernel")
            else:
                pass
    
    def load_kernel(self, timestamp, dir_path:str|None=None):
        """load logger kernel via timestamp"""
        self.lock.acquire()
        dir_path = self.dir_path if dir_path is None else dir_path

        kernel_path = f"{dir_path}/kernel_{timestamp}.pkl"
        self.kernel = Logger_Kernel.load(kernel_path)
        net_path = f"{dir_path}/{self.kernel.logfile_info['net']}"
        self.net_storager.load(self.net, net_path)

        if (self.optim is not None) and ("optim" in self.kernel.logfile_info):
            optim_path = f"{dir_path}/{self.kernel.logfile_info['optim']}"
            self.optim_storager.load(self.optim, optim_path)
        if (self.lr_scheduler_list is not None) and ("lr_scheduler" in self.kernel.logfile_info):
            lr_scheduler_path = f"{dir_path}/{self.kernel.logfile_info['lr_scheduler']}"
            self.lr_scheduler_storager.load(self.lr_scheduler_list, lr_scheduler_path)
        
        self.lock.release()
    
    def new_kernel(self):
        """create new logger kernel"""
        self.lock.acquire()

        self.kernel = Logger_Kernel()
        self.kernel.update_extra_info(epoch=0, avg_loss=-1.0)

        self.lock.release()
    
    def print_info(self):
        """echo logger kernel info"""
        epoch = self.kernel.extra_info["epoch"]
        epoch_avg_loss = self.kernel.extra_info["avg_loss"]
        print(f'epoch: {epoch}, epoch_avg_loss: {epoch_avg_loss}')
    
    def log_train(self, epoch, loss, acc):
        """logging training data"""
        with self.lock:
            self.train_logger.set_head(["epoch", "loss", "acc"])
            self.train_logger.add([epoch, loss, acc])
    
    def log_eval(self, epoch, loss, acc):
        """logging eval data"""
        with self.lock:
            self.eval_logger.set_head(["epoch", "loss", "acc"])
            self.eval_logger.add([epoch, loss, acc])
    
    def update_avg_loss(self, avg_loss):
        """logging loss data"""
        with self.lock:
            self.kernel.update_extra_info(avg_loss=avg_loss)
    
    def _load_train_and_eval(self, timestamp):
        with self.lock:
            (name, data_list) = self._get_log("train", timestamp=timestamp)
            self.train_logger.set_head(name)
            if data_list is not None:
                for data in data_list:
                    self.train_logger.add(data)

            (name, data_list) = self._get_log("eval", timestamp=timestamp)
            self.eval_logger.set_head(name)
            if data_list is not None:
                for data in data_list:
                    self.eval_logger.add(data)
    
    def add_epoch(self, epochs=1):
        """logging now epoch"""
        with self.lock:
            if 'epoch' in self.kernel.extra_info:
                kernel_epoch = self.kernel.extra_info['epoch']
            else:
                kernel_epoch = 0
            self.kernel.update_extra_info(epoch= kernel_epoch + epochs)
    
    def get_epoch(self):
        """return epoch"""
        return self.kernel.extra_info["epoch"]
    
    def get_avg_loss(self):
        """return avg loss"""
        return self.kernel.extra_info["avg_loss"]
    
    def save(self):
        """start a thread to save all data in eval epoch"""
        if self.thread_save:
            thread = threading.Thread(
                target=self._save_thread,
                kwargs=dict(
                    temp_save=False
                )
            )
            thread.start()
        else:
            self._save_thread(temp_save=False)

    def save_temp(self):
        """start a thread to save all data in all epoch"""
        if self.thread_save:
            thread = threading.Thread(
                target=self._save_thread,
                kwargs=dict(
                    temp_save=True
                )
            )
            thread.start()
        else:
            self._save_thread(temp_save=True)
    
    def _del_files(self, timestamp):
        files_key = (
            "train_log",
            "eval_log",
            "net",
            "optim",
            "lr_scheduler"
        )
        root = self.dir_path
        kernel_filename = f"kernel_{timestamp}.pkl"
        kernel_filepath = f"{root}/{kernel_filename}"

        kernel = Logger_Kernel.load(kernel_filepath)
        for key in files_key:
            if key in kernel.logfile_info:
                filename = kernel.logfile_info[key]
                filepath = f"{root}/{filename}"
                os.remove(filepath)

        os.remove(kernel_filepath)

    def _save_thread(self, temp_save=False):
        self.lock.acquire()

        # to avoid the same timestamp, we sleep 1.1sec
        sleep(1.1)

        now_time = datetime.now()
        timestamp = now_time.strftime("%Y%m%d%H%M%S")
        timestamp_human = now_time.strftime("%Y-%m-%d_%H-%M-%S")

        kernel_filename = f"kernel_{timestamp}.pkl"
        epoch = self.kernel.extra_info['epoch']
        train_filename = f"train_log_{timestamp_human}_epoch-{epoch}.csv"
        eval_filename = f"eval_log_{timestamp_human}_epoch-{epoch}.csv"
        net_filename = f"net_{timestamp_human}_epoch-{epoch}.pt"
        optim_filename = f"optim_{timestamp_human}_epoch-{epoch}.pt"
        lr_scheduler_filename = f"lr_scheduler_{timestamp_human}_epoch-{epoch}.pt"

        kernel_filepath = f"{self.dir_path}/{kernel_filename}"
        train_filepath = f"{self.dir_path}/{train_filename}"
        eval_filepath = f"{self.dir_path}/{eval_filename}"
        net_filepath = f"{self.dir_path}/{net_filename}"
        optim_filepath = f"{self.dir_path}/{optim_filename}"
        lr_scheduler_filepath = f"{self.dir_path}/{lr_scheduler_filename}"

        if temp_save:
            self.train_logger.save(train_filepath, clear_buffer=False)
            self.eval_logger.save(eval_filepath, clear_buffer=False)
        else:
            self.train_logger.save(train_filepath)
            self.eval_logger.save(eval_filepath)
        self.net_storager.save(self.net, net_filepath)

        self.kernel.update_logfile_info(train_log=train_filename, net=net_filename, eval_log=eval_filename)

        if self.optim is not None:
            self.kernel.update_logfile_info(optim=optim_filename)
            self.optim_storager.save(self.optim, optim_filepath)
        if self.lr_scheduler_list is not None:
            self.kernel.update_logfile_info(lr_scheduler=lr_scheduler_filename)
            self.lr_scheduler_storager.save(self.lr_scheduler_list, lr_scheduler_filepath)

        # save snap
        using_temp_kernel = self.using_temp_kernel
        if using_temp_kernel:
            temp_kernel_timestamp = self.kernel.extra_info["temp_kernel_timestamp"]

        if temp_save:
            self.kernel.update_extra_info(temp_kernel=True, temp_kernel_timestamp=timestamp)
            self.using_temp_kernel = True
            Logger_Kernel.save(self.kernel, kernel_filepath)
        else:
            self.kernel.update_history(timestamp)
            self.kernel.update_extra_info(temp_kernel=False)
            self.using_temp_kernel = False
            Logger_Kernel.save(self.kernel, kernel_filepath)
        
        if using_temp_kernel:
            self._del_files(temp_kernel_timestamp)

        self.lock.release()
    
    def _get_log(self, log_type, timestamp):
        kernel_path = f"{self.dir_path}/kernel_{timestamp}.pkl"
        history_kernel = Logger_Kernel.load(kernel_path)
        history_log_filename = history_kernel.logfile_info[f"{log_type}_log"]
        history_log_path = f"{self.dir_path}/{history_log_filename}"
        (name, data) = self.plot_logger.read(history_log_path)
        return (name, data)

    def get_all_log(self, log_type):
        """get all training or eval log info from epoch=0 to now"""
        assert log_type in ["eval", "train"]
        name_array, data_array = [], []
        kernel_history_timestamp_array = self.kernel.kernel_history
        for history_timestamp in kernel_history_timestamp_array:
            (name, data) = self._get_log(log_type, timestamp=history_timestamp)
            if name is not None and data is not None:
                name_array = name
                data_array = data_array + data
        data_np = np.array(data_array, dtype=float).T
        return (name_array, data_np)
    
    def print_log(self, log_type):
        """output log via console echo"""
        assert log_type in ["eval", "train"]
        name_array, data_np = self.get_all_log(log_type)
        [name_epoch, name_loss, name_acc] = name_array
        [data_epoch, data_loss, data_acc] = data_np

        print(f"{'':=<18}{log_type.upper():=<23}")
        print(f"| {name_epoch: <6} | {name_loss: <15} | {name_acc: <10} |")
        print(f"{'':-<41}")
        for (epoch, loss, acc) in zip(data_epoch, data_loss, data_acc):
            print(f"| {int(epoch): <6d} | {float(loss): <15f} | {acc: <10f} |")
        print(f"{'':-<41}")
    
    def plot_log(self, log_type, plot_method, save_path=None, figsize=(12, 6), loss_ylim=None, acc_ylim=None):
        """output log via matplotlib.pyplot"""
        assert log_type in ["eval", "train"]
        assert plot_method in ["show", "save"]
        name_array, data_np = self.get_all_log(log_type)
        [name_epoch, name_loss, name_acc] = name_array
        [data_epoch, data_loss, data_acc] = data_np

        plt.figure(figsize=figsize)

        plt.subplot(121)
        plt.plot(data_epoch, data_loss)
        plt.xlabel(name_epoch)
        plt.ylabel(name_loss)
        plt.title(f"{log_type} {name_loss}")
        plt.grid(True)
        if loss_ylim is not None:
            plt.ylim(loss_ylim)

        plt.subplot(122)
        plt.plot(data_epoch, data_acc)
        plt.xlabel(name_epoch)
        plt.ylabel(name_acc)
        plt.title(f"{log_type} {name_acc}")
        plt.grid(True)
        if acc_ylim is not None:
            plt.axis(acc_ylim)

        if plot_method == "show":
            plt.show()
        elif plot_method == "save":
            assert save_path is not None
            plt.savefig(save_path)
        
class MetricsLogger(Logger):
    """Logger which can save metrics info"""
    def log_train(self, epoch, **metrics):
        """logging training data"""
        with self.lock:
            metrics_keys = list(metrics.keys())
            metrics_values = list(metrics.values())
            assert "loss" in metrics_keys

            heads = ["epoch"] + metrics_keys
            values = [epoch] + metrics_values
            self.train_logger.set_head(heads)
            self.train_logger.add(values)

    def log_eval(self, epoch, **metrics):
        """logging eval data"""
        with self.lock:
            metrics_keys = list(metrics.keys())
            metrics_values = list(metrics.values())
            assert "loss" in metrics_keys

            heads = ["epoch"] + metrics_keys
            values = [epoch] + metrics_values
            self.eval_logger.set_head(heads)
            self.eval_logger.add(values)

    def plot_log(self, log_type, plot_method, max_column_num=5, save_path=None, figsize=(12, 6), **metrics_ylim):
        """output log via matplotlib.pyplot"""
        assert log_type in ["eval", "train"]
        assert plot_method in ["show", "save"]
        name_array, data_np = self.get_all_log(log_type)

        (name_epoch, name_metrics) = (name_array[0], name_array[1:])
        (data_epoch, data_metrics) = (data_np[0], data_np[1:])

        plot_figure_num = len(name_metrics) 
        if plot_figure_num < max_column_num:
            row_num = 1
            column_num = plot_figure_num
        elif plot_figure_num % max_column_num == 0:
            row_num = plot_figure_num // max_column_num
            column_num = max_column_num
        else:
            row_num = plot_figure_num // max_column_num + 1
            column_num = max_column_num

        plt.figure(figsize=figsize)

        for index in range(plot_figure_num):
            metrics_name = name_metrics[index]
            metrics_data = data_metrics[index]

            plt.subplot(row_num, column_num, index+1)
            plt.plot(data_epoch, metrics_data)
            plt.xlabel(name_epoch)
            plt.ylabel(metrics_name)
            plt.title(f"{log_type} {metrics_name}")
            plt.grid(True)
            ylim_key = f"{metrics_name}_ylim"
            if ylim_key in metrics_ylim:
                plt.ylim(metrics_ylim[ylim_key])

        if plot_method == "show":
            plt.show()
        elif plot_method == "save":
            assert save_path is not None
            plt.savefig(save_path)
 