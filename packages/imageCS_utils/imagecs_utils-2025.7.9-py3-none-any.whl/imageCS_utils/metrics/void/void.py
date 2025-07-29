import torch

def void_func(*args, **kwargs):
    return torch.zeros((1,), dtype=torch.float32)