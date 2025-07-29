import torch

def psnr(X, Y, data_range=1.0):
    data_range = torch.tensor(data_range)
    mse = torch.mean((X - Y)**2)
    return 20 * torch.log10(data_range) - 10 * torch.log10(mse)