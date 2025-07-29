"""Base class for network training, containing all information in Base class to facilitate subsequent debugging and calling"""
# pylint: disable=invalid-name
import os
from typing import Type, Dict, List, Any, Optional

import torch
from torch import nn
from torch.utils.data.dataloader import DataLoader as DataLoaderClass
from torch.utils.data.dataset import Dataset as DatasetClass
import torchvision

from .seed import seed_everything
from .info import Info
from .status import TrainStateWriter
from .shared_utils import init_folder_path
from ..old_pretrained_compatible import pretrained_old2new

from .gpu_holder import GPUHolder
from .Logger import Logger as LoggerClass
from .trainer import MetricsTrainer as TrainerClass

class AttrDataParallel(torch.nn.DataParallel):
    """Fix the problem of the DataParallel cannot attribute Module's var and func"""
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.module, name)

class Base:
    """Base class for network training, containing all information in Base class to facilitate subsequent debugging and calling"""
    def __init__(self, gpu_num:int|List[int], Net:Type[nn.Module], Logger:Type[LoggerClass],
                 Loss:Type[nn.Module]|Type[Any], Opt:Type[torch.optim.Optimizer], Trainer:Type[TrainerClass],
                 logger_path:str, net_kwargs:Dict[str, Any], loss_kwargs:Dict[str, Any], opt_kwargs:Dict[str, Any], cfg:dict,
                 trainer_kwargs:Optional[Dict[str, Any]]=None,
                 LR_Scheduler_list:List[Type[torch.optim.lr_scheduler.LRScheduler]]|None=None, lr_scheduler_kwargs_list:List[Dict[str, Any]]|None=None, lr_scheduler_milestones_list:List[int]|None=None,
                 Monitor:Type[TrainStateWriter]=TrainStateWriter, monitor_kwargs:Dict[str, Any]|None=None,
                 GPU_holder:Type[GPUHolder] = GPUHolder, gpu_holder_kwargs:Optional[Dict[str, Any]]=None,
                 seed:Optional[int]=None, use_compile:bool=True, log_timestamp:Optional[int]=None, log_rollback_epoch:Optional[int]=None,
                 no_monitor:bool=False, no_gpu_holder:bool=False):

        # set default value using these code instead of using dangerous-default-value
        trainer_kwargs = {} if trainer_kwargs is None else trainer_kwargs
        lr_scheduler_kwargs_list = [] if lr_scheduler_kwargs_list is None else lr_scheduler_kwargs_list
        monitor_kwargs = {} if monitor_kwargs is None else monitor_kwargs
        gpu_holder_kwargs = {} if gpu_holder_kwargs is None else gpu_holder_kwargs
        
        # init
        self.gpu_num = gpu_num
        self.Net = Net
        self.Logger = Logger
        self.Loss = Loss
        self.Opt = Opt
        self.Trainer = Trainer
        self.Monitor = Monitor
        self.GPU_holder = GPU_holder

        self.logger_path = logger_path
        self.net_kwargs = net_kwargs
        self.loss_kwargs = loss_kwargs
        self.opt_kwargs = opt_kwargs
        self.trainer_kwargs = trainer_kwargs
        self.monitor_kwargs = monitor_kwargs

        gpu_holder_kwargs["gpu_num"] = self.gpu_num
        self.gpu_holder_kwargs = gpu_holder_kwargs

        self.seed = seed
        self.use_compile = use_compile
        self.log_timestamp = log_timestamp
        self.log_rollback_epoch = log_rollback_epoch
        self.cfg = cfg
        self.no_monitor = no_monitor
        self.no_gpu_holder = no_gpu_holder

        self.LR_Scheduler_list = LR_Scheduler_list
        self.lr_scheduler_kwargs_list = lr_scheduler_kwargs_list
        self.lr_scheduler_milestones_list = lr_scheduler_milestones_list

        self.dataloader_test_dict:Dict[str, DataLoaderClass] = {}

        self.monitor = None
        self.gpu_holder = None

        self._set_device()
        self._set_seed()
        self._init_base()
        self._addition_operation()
    
    def _set_device(self):
        assert type(self.gpu_num) in [int, list]
        if isinstance(self.gpu_num, int):
            if self.gpu_num < 0:
                os.environ["CUDA_VISIBLE_DEVICES"] = ""
                self.dev = torch.device("cpu")
            else:
                os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
                os.environ["CUDA_VISIBLE_DEVICES"] = str(self.gpu_num)
                self.dev = torch.device("cuda:0")
        else:
            set_str = ""
            for gpu_num in self.gpu_num:
                gpu_num = str(gpu_num)
                set_str += gpu_num + ","
            os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
            os.environ["CUDA_VISIBLE_DEVICES"] = set_str
            self.dev = torch.device("cuda:0")
    
    def _init_base(self):
        self._init_net()
        self._init_opt()
        self._init_lr_scheduler()
        self._init_logger()
        self._init_loss()
        self._init_trainer()
        if not self.no_monitor:
            self._init_monitor()
        if not self.no_gpu_holder:
            self._init_gpu_holder()
    
    def _set_seed(self):
        if self.seed is not None:
            seed_everything(self.seed)

    def _init_net(self):
        if isinstance(self.gpu_num, int):
            self.net = self.Net(**self.net_kwargs)
            self.net = self.net.to(self.dev)
        else:
            self.net = self.Net(**self.net_kwargs)
            self.net = AttrDataParallel(self.net)
            self.net = self.net.to(self.dev)
        
        if int(torch.__version__[0]) >= 2 and self.use_compile:
            # pytorch2.0 and last
            self.net = torch.compile(self.net)
            Info.warn(f"Using torch.compile in pytorch-{torch.__version__}")
    
    def _init_logger(self):
        if self.log_timestamp is None:
            self.logger = self.Logger(self.logger_path, self.net, optim=self.opt, lr_scheduler_list=self.lr_scheduler_list, load_newest=True, rollback_epoch=self.log_rollback_epoch)
        else:
            self.logger = self.Logger(self.logger_path, self.net, optim=self.opt, lr_scheduler_list=self.lr_scheduler_list, timestamp=self.log_timestamp, load_newest=False, rollback_epoch=self.log_rollback_epoch)
    
    def _init_loss(self):
        self.loss = self.Loss(**self.loss_kwargs)
    
    def _init_opt(self):
        self.opt = self.Opt(self.net.parameters(), **self.opt_kwargs)
    
    def _init_trainer(self):
        self.trainer = self.Trainer(self.net, self.loss, self.opt, self.dev, self.logger, lr_scheduler_list=self.lr_scheduler_list, **self.trainer_kwargs)
    
    def _init_lr_scheduler(self):
        if self.LR_Scheduler_list is None:
            self.lr_scheduler_list:None = None
        else:
            assert len(self.LR_Scheduler_list) == len(self.lr_scheduler_kwargs_list)
            lr_scheduler_list:List[torch.optim.lr_scheduler.LRScheduler] = []
            for (LR_Scheduler, lr_scheduler_kwargs) in zip(self.LR_Scheduler_list, self.lr_scheduler_kwargs_list):
                lr_scheduler_list.append(LR_Scheduler(optimizer=self.opt, **lr_scheduler_kwargs))
            
            if self.lr_scheduler_milestones_list is None:
                self.lr_scheduler_list = lr_scheduler_list
            else:
                lr_scheduler = torch.optim.lr_scheduler.SequentialLR(
                    optimizer = self.opt,
                    schedulers = lr_scheduler_list,
                    milestones = self.lr_scheduler_milestones_list
                )
                self.lr_scheduler_list = [lr_scheduler]
    
    def _init_monitor(self):
        self.monitor = self.Monitor(monitored_base=self, **self.monitor_kwargs)
    
    def _init_gpu_holder(self):
        self.gpu_holder = self.GPU_holder(**self.gpu_holder_kwargs)

    def _addition_operation(self):
        """addition operation when init class, you can change it in subclass"""
    
    def set_dataset(self, Dataset:Type[DatasetClass], dataset_kwargs:dict, dtype:str):
        """set dataset (dtype is train or val)"""
        assert dtype in ["train", "val"]
        if dtype == "train":
            self.dataset_train = Dataset(**dataset_kwargs)
        elif dtype == "val":
            self.dataset_val = Dataset(**dataset_kwargs)
    
    def set_dataloader(self, DataLoader:Type[DataLoaderClass], dataloader_kwargs:dict, dtype:str):
        """set dataloader (dtype is train or val), you should run self.set_dataset first"""
        assert dtype in ["train", "val"]
        if dtype == "train":
            self.dataloader_train = DataLoader(self.dataset_train, **dataloader_kwargs)
        elif dtype == "val":
            self.dataloader_val = DataLoader(self.dataset_val, **dataloader_kwargs)
    
    def _append_test_dataloader(self, Dataset, DataLoader, dataset_kwargs, dataloader_kwargs, dataset_name):
        dataset_test = Dataset(**dataset_kwargs)
        dataloader_test = DataLoader(dataset_test, **dataloader_kwargs)

        self.dataloader_test_dict[dataset_name] = dataloader_test
    
    def append_test_dataloader(self, **cfg_dict):
        """add test dataloader"""
        for dataset_name, cfg in cfg_dict.items():
            self._append_test_dataloader(**cfg, dataset_name=dataset_name)
    
    def addition_setting(self):
        """If you have extra steps, you can rewrite this function in a subclass"""
    
    def add_cfg(self, cfg):
        """deprecated function"""
        raise RuntimeError("add_cfg fuction is deprecated, please pass in the cfg parameter directly when the Base class is initialized.")
    
    def train(self, compare_func, checkpoint_epoch=50, eval_epoch=10, epochs=1000):
        """start training"""
        if not self.no_monitor:
            self.monitor.start()

        if not self.no_gpu_holder:
            self.gpu_holder.start()
            self.trainer.train(self.dataloader_train, self.dataloader_val, compare_func, checkpoint_epoch, eval_epoch, epochs, self.gpu_holder)
            self.gpu_holder.stop()
        else:
            self.trainer.train(self.dataloader_train, self.dataloader_val, compare_func, checkpoint_epoch, eval_epoch, epochs)

        if not self.no_monitor:
            self.monitor.stop()
    
    def test(self, dataloader_test, metrics_func_dict):
        "start testing"
        return self.trainer.test(dataloader_test, metrics_func_dict)

    def save_metrics_plot(self, save_root, figsize=(12, 6)):
        """save metrics matplotlib.pyplot"""
        init_folder_path(save_root, overwrite=True)

        self.logger.plot_log(
            log_type = "train",
            plot_method = "save",
            save_path = f"{save_root}/train.png",
            figsize=figsize
        )
        self.logger.plot_log(
            log_type = "eval",
            plot_method = "save",
            save_path = f"{save_root}/val.png",
            figsize=figsize
        )
    
    def get_params(self):
        """get module's params"""
        total_params = sum(param.numel() for param in self.net.parameters())
        trainable_params = sum(param.numel() for param in self.net.parameters() if param.requires_grad)

        return (total_params, trainable_params)


    
class MetricsBase(Base):
    """
    Base class for network training, containing all information in MetricsBase class to facilitate subsequent debugging and calling
    Different from Base class, you can use MetricsTrainer or UniversalMetricsTrainer in this class
    """
    def train(self, metrics_func_dict, checkpoint_epoch=50, eval_epoch=10, epochs=1000):
        if not self.no_monitor:
            self.monitor.start()

        if not self.no_gpu_holder:
            self.gpu_holder.start()
            self.trainer.train(self.dataloader_train, self.dataloader_val, metrics_func_dict, checkpoint_epoch, eval_epoch, epochs, self.gpu_holder)
            self.gpu_holder.stop()
        else:
            self.trainer.train(self.dataloader_train, self.dataloader_val, metrics_func_dict, checkpoint_epoch, eval_epoch, epochs)

        if not self.no_monitor:
            self.monitor.stop()
    
class TestBase(Base):
    """Base class which only used for test pre-trained model"""
    def __init__(self, gpu_num:int|List[int], Net:Type[nn.Module], Trainer:Type[TrainerClass], net_pretrained_path:str, cfg:dict,
                 net_kwargs:Dict[str, Any], trainer_kwargs:Optional[Dict[str, Any]]=None, 
                 seed:Optional[int]=None, use_compile:bool=True):
        # init
        self.gpu_num = gpu_num
        self.Net = Net
        self.Trainer = Trainer

        self.net_kwargs = net_kwargs
        self.trainer_kwargs = trainer_kwargs

        self.net_predtrained_path = net_pretrained_path

        self.seed = seed
        self.use_compile = use_compile
        self.cfg = cfg

        self.dataloader_test_dict:Dict[str, DataLoaderClass] = {}

        self.monitor = None
        self.gpu_holder = None

        self._set_device()
        self._set_seed()
        self._init_base()
        self._addition_operation()

    def _init_base(self):
        self._init_net()
        self._init_trainer()

    def _init_trainer(self):
        self.trainer = self.Trainer(
            net = self.net,
            dev = self.dev,
            loss = None,
            opt = None,
            logger = None,
            **self.trainer_kwargs
        )

        self.trainer._loss_forward = lambda data_prepare_output, net_forward_output : torch.tensor([0.0], dtype=torch.float32)
    
    def _net_parallel(self):
        if isinstance(self.gpu_num, int):
            self.net = self.Net(**self.net_kwargs)
        else:
            self.net = self.Net(**self.net_kwargs)
            self.net = AttrDataParallel(self.net)
    
    def _net_prepare_pretrained(self):
        state_dict = torch.load(self.net_predtrained_path, map_location=torch.device("cpu"))
        return state_dict
    
    def _net_load_pretrained(self, state_dict):

        try:
            self.net.load_state_dict(state_dict)
        except:
            # old pretrained model
            Info.warn("Error on new type of pretrained model, trying old type...")
            Info.warn(f"[new type]\n{state_dict.keys()}")
            state_dict = pretrained_old2new(state_dict)
            Info.warn(f"[old type]\n{state_dict.keys()}")
            self.net.load_state_dict(state_dict)

    def _net_compile(self):
        if int(torch.__version__[0]) >= 2 and self.use_compile:
            # pytorch2.0 and last
            self.net = torch.compile(self.net)
            Info.warn(f"Using torch.compile in pytorch-{torch.__version__}")
    
    def _init_net(self):
        self._net_parallel()
        state_dict = self._net_prepare_pretrained()
        self._net_load_pretrained(state_dict)
        self.net = self.net.to(self.dev)
        self._net_compile()

    def save_metrics_plot(self, save_root):
        raise NotImplementedError("This function is not avaliable for TestBase")
    
    def train(self, compare_func, checkpoint_epoch=50, eval_epoch=10, epochs=1000):
        raise NotImplementedError("This function is not avaliable for TestBase")
    
