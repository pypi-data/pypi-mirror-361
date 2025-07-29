# Generate Config, easy to change

from dataclasses import dataclass
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

from .gpu_holder import GPUHolder
from .Logger import Logger as LoggerClass
from .trainer import MetricsTrainer as TrainerClass
from .base import Base as BaseClass
from .base import TestBase as TestBaseClass


########################## Base Config ##########################
@dataclass
class MapKwargsMap_Abstract:
    data_prepare_output:dict[str, str]
    net_forward_output:dict[str, str]

    def to_dict(self):
        return vars(self)

LossKwargsMap = MapKwargsMap_Abstract
MetricsKwargsMap = MapKwargsMap_Abstract

@dataclass
class TrainerKwargs:
    data_prepare_output_keys:list[str]
    net_forward_output_keys:list[str]
    to_dev_keys:list[str]
    batch_size_sample_key:str
    net_kwargs_map:dict[str, str]
    loss_kwargs_map:LossKwargsMap
    other_data_dict:dict

    def to_dict(self):
        cfg = vars(self)
        cfg["loss_kwargs_map"] = self.loss_kwargs_map.to_dict()
        return cfg

@dataclass
class UniversalTrainerKwargs(TrainerKwargs):
    metrics_kwargs_map:dict[str, MetricsKwargsMap]
    metrics_kwargs_config:dict[str, dict]
    ignore_training_metrics:list[str]

    def to_dict(self):
        cfg = super().to_dict()
        for metrics_name in cfg["metrics_kwargs_map"]:
            cfg["metrics_kwargs_map"][metrics_name] = self.metrics_kwargs_map[metrics_name].to_dict()
        return cfg

@dataclass
class BaseConfig:
    Net:Type[nn.Module]
    Logger:Type[LoggerClass]
    Loss:Type[nn.Module]|Type[Any]
    Opt:Type[torch.optim.Optimizer]
    Trainer:Type[TrainerClass]
    logger_path:str
    net_kwargs:Dict[str, Any]
    loss_kwargs:Dict[str, Any]
    opt_kwargs:Dict[str, Any]
    trainer_kwargs:TrainerKwargs
    LR_Scheduler_list:List[Type[torch.optim.lr_scheduler.LRScheduler]]|None=None
    lr_scheduler_kwargs_list:List[Dict[str, Any]]|None=None
    lr_scheduler_milestones_list:List[int]|None=None
    Monitor:Type[TrainStateWriter]=TrainStateWriter
    monitor_kwargs:Dict[str, Any]|None=None
    GPU_holder:Type[GPUHolder] = GPUHolder
    gpu_holder_kwargs:Optional[Dict[str, Any]]=None
    seed:Optional[int]=None
    use_compile:bool=False
    no_monitor:bool=False
    no_gpu_holder:bool=False

    def to_dict(self):
        cfg = vars(self)
        cfg["trainer_kwargs"] = self.trainer_kwargs.to_dict()

        return cfg

@dataclass
class TestBaseConfig:
    Net:Type[nn.Module]
    Trainer:Type[TrainerClass]
    net_kwargs:Dict[str, Any]
    trainer_kwargs:TrainerKwargs | UniversalTrainerKwargs
    net_pretrained_path:str
    seed:Optional[int]=None
    use_compile:bool=False

    def to_dict(self):
        cfg = vars(self)
        cfg["trainer_kwargs"] = self.trainer_kwargs.to_dict()

        return cfg

########################## Dataset Config ##########################

@dataclass
class __DatasetConfig:
    Dataset:Type[DatasetClass]
    DataLoader:Type[DataLoaderClass]
    dataset_kwargs:dict
    dataloader_kwargs:dict

    def to_dataset_dict(self, dtype:str|None):
        assert dtype in ["train", "val", None]
        cfg = {
            "Dataset": self.Dataset,
            "dataset_kwargs": self.dataset_kwargs,
        }
        if dtype is not None:
            cfg["dtype"] = dtype

        return cfg
    
    def to_dataloader_dict(self, dtype:str|None):
        assert dtype in ["train", "val", None]
        cfg = {
            "DataLoader": self.DataLoader,
            "dataloader_kwargs": self.dataloader_kwargs,
        }
        if dtype is not None:
            cfg["dtype"] = dtype

        return cfg

class DatasetTrainConfig(__DatasetConfig):
    def to_dataset_dict(self):
        return super().to_dataset_dict("train")
    def to_dataloader_dict(self):
        return super().to_dataloader_dict("train")

class DatasetValConfig(__DatasetConfig):
    def to_dataset_dict(self):
        return super().to_dataset_dict("val")
    def to_dataloader_dict(self):
        return super().to_dataloader_dict("val")

@dataclass
class DatasetTestConfig(__DatasetConfig):
    dataset_name:str

    def to_dict(self):
        dataset_dict = super().to_dataset_dict(None)
        dataloader_dict = super().to_dataloader_dict(None)

        cfg = dataset_dict | dataloader_dict
        return cfg

@dataclass
class DatasetTestDictConfig:
    dataset_test_config_list: List[DatasetTestConfig]

    def to_dict(self):
        cfg = {}
        for dataset_test_config in self.dataset_test_config_list:
            cfg[dataset_test_config.dataset_name] = dataset_test_config.to_dict()
        return cfg

########################## Train Config ##########################
@dataclass
class TrainConfig:
    epochs:int
    checkpoint_epoch:int
    eval_epoch:int
    metrics_func_dict:dict

    def to_dict(self):
        return vars(self)

########################## Main Config ##########################
@dataclass
class MainConfig:
    Base:Type[BaseClass]
    base_config:BaseConfig
    dataset_train_config:DatasetTrainConfig
    dataset_val_config:DatasetValConfig
    dataset_test_dict_config:DatasetTestDictConfig
    train_config:TrainConfig
    addition_params:dict|None = None

    def gen_cfg(self):
        cfg = dict()
        cfg["Base"] = self.Base
        cfg["base_config"] = self.base_config.to_dict()
        cfg["dataset_train_config"] = self.dataset_train_config.to_dataset_dict()
        cfg["dataloader_train_config"] = self.dataset_train_config.to_dataloader_dict()
        cfg["dataset_val_config"] = self.dataset_val_config.to_dataset_dict()
        cfg["dataloader_val_config"] = self.dataset_val_config.to_dataloader_dict()
        cfg["test_config"] = self.dataset_test_dict_config.to_dict()
        cfg["train_config"] = self.train_config.to_dict()
        cfg["addition_params"] = self.addition_params

        return cfg

@dataclass
class TestConfig:
    Base:Type[TestBaseClass]
    base_config:TestBaseConfig
    dataset_test_dict_config:DatasetTestDictConfig
    train_config:TrainConfig
    addition_params:dict|None = None

    def gen_cfg(self):
        cfg = dict()
        cfg["Base"] = self.Base
        cfg["base_config"] = self.base_config.to_dict()
        cfg["test_config"] = self.dataset_test_dict_config.to_dict()
        cfg["train_config"] = self.train_config.to_dict()
        cfg["addition_params"] = self.addition_params

        return cfg
