import torch
from .base_utils.Logger import get_state_dict

def _get_model(cfg_dict:dict, device=torch.device("cpu")):
    Model = cfg_dict["base_config"]["Net"]
    model_kwargs = cfg_dict["base_config"]["net_kwargs"]

    model:torch.nn.Module = Model(**model_kwargs).to(device)
    return model

def _get_statedict_via_path(pt_path:str, device=torch.device("cpu")):
    state_dict = torch.load(pt_path, map_location=device)
    return state_dict

def _get_statedict_via_logger(cfg_dict:dict, timestamp:int|None=None, device=torch.device("cpu")):
    logger_folder = cfg_dict["base_config"]["logger_path"]
    state_dict = get_state_dict(logger_folder=logger_folder, timestamp=timestamp, dev=device)
    return state_dict

def get_pretrained_model_via_logger(cfg_dict:dict,  timestamp:int|None=None, device=torch.device("cpu")):
    model = _get_model(cfg_dict, device)
    state_dict = _get_statedict_via_logger(cfg_dict, timestamp, device)
    model.load_state_dict(state_dict)
    return model

def get_pretrained_model_via_path(cfg_dict:dict, pt_path:str, device=torch.device("cpu")):
    model = _get_model(cfg_dict, device)
    state_dict = _get_statedict_via_path(pt_path, device)
    model.load_state_dict(state_dict)
    return model

