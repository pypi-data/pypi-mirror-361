from skimage.metrics import structural_similarity as ssim_func
from .ssim import _3d_to_4d_tensors
import torch
import numpy as np

def _tensor2ndarray(X:torch.Tensor):
    r""" PyTorch format to Numpy format ()
    Args:
        X (torch.Tensor): (B,C,H,W)

    Returns:
        X (numpy.float32): (B,C,H,W)
    """
    assert len(X.size()) == 4

    X = X.numpy().astype(np.float64)
    return X

def ssim(X:torch.Tensor, Y:torch.Tensor, addition_func=None, data_range=1):
    r""" interface of ssim
    Args:
        X (torch.Tensor): a batch of images, (N,C,H,W)
        Y (torch.Tensor): a batch of images, (N,C,H,W)
        data_range (float or int, optional): value range of input images. (usually 1.0 or 255)

    Returns:
        torch.Tensor: ssim results
    """
    assert X.size() == Y.size()
    X = X.cpu().detach()
    Y = Y.cpu().detach()

    data_num = X.size(0)

    X = _3d_to_4d_tensors(X)
    Y = _3d_to_4d_tensors(Y)

    X = _tensor2ndarray(X)
    Y = _tensor2ndarray(Y)

    if addition_func is not None:
        X = addition_func(X)
        Y = addition_func(Y)
    
    ssim_mean = sum([float(ssim_func(X[bs], Y[bs], data_range=data_range, channel_axis=0)) for bs in range(data_num)])
    ssim_mean = ssim_mean / data_num
    

    ssim_mean = torch.tensor(ssim_mean)

    return ssim_mean