import torch
from torch import Tensor
import torch.nn.functional as F
from einops import rearrange

def batch_conv2d(x:Tensor, kernel:Tensor, stride:int|tuple[int, int], padding:int|tuple[int, int], bias:Tensor|None=None):
    """ Batch Convolution

    Args:
        x (Tensor): Size[bs, c_in, h, w]
        kernel (Tensor): Size[bs, c_out, c_in, kernel_h, kernel_w]
        stride (int | tuple[int, int]): stride
        padding (int | tuple[int, int]): padding
        bias (Tensor | None, optional): Size[bs c_out] if is not None. Defaults to None.

    Returns:
        Tensor: Size[bs, c_out, h, w]
    """
    # init
    (x_bs, x_c, x_h, x_w) = x.size()
    (k_bs, k_out, k_in, k_h, k_w) = kernel.size()
    assert x_bs == k_bs
    assert x_c == k_in

    if bias is not None:
        (b_bs, b_c) = bias.size()
        assert b_bs == k_bs
        assert b_c == k_out
    
    # encode
    x = rearrange(x, "(new_bs bs) c h w -> new_bs (bs c) h w", new_bs=1)
    kernel = rearrange(kernel, "bs c_out c_in h w -> (bs c_out) c_in h w")
    if bias is not None:
        bias = rearrange(bias, "bs c -> (bs c)")


    # batch conv
    x = F.conv2d(
        input = x,
        weight = kernel,
        bias = bias,
        stride = stride,
        padding = padding,
        groups = x_bs
    )
    
    # decode
    out = rearrange(x, "new_bs (bs c) h w -> (new_bs bs) c h w", bs=x_bs)

    # return
    return out
