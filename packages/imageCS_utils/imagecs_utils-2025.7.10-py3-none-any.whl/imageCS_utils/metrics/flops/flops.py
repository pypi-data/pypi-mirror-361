from thop import profile
from ...utils import to_2tuple

def get_flops(model, inputs):
    macs, params = profile(model, inputs)
    flops = macs * 2
    return flops

def get_macs(model, inputs):
    macs, params = profile(model, inputs)
    return macs

class Calculate_FLOPs:
    @staticmethod
    def cnn(img_size:int|tuple[int, int], in_channels:int, out_channels:int, kernel_size:int|tuple[int, int], stride:int|tuple[int, int], padding:int|tuple[int, int], bias:bool):
        img_size = to_2tuple(img_size)
        kernel_size = to_2tuple(kernel_size)
        stride = to_2tuple(stride)
        padding = to_2tuple(padding)

        img_size = (img_size[0] + padding[0], img_size[1] + padding[1])

        # one step conv
        conv_kernel_mul = kernel_size[0] * kernel_size[1] * in_channels * out_channels
        conv_kernel_add = kernel_size[0] * kernel_size[1] * out_channels - 1
        conv_kernel = conv_kernel_add + conv_kernel_mul

        # calculate n step
        (h_out, w_out) = ((img_size[0]-kernel_size[0]) // stride[0],  (img_size[1]-kernel_size[1]) // stride[1])

        # calculate all
        FLOPs = h_out * w_out * conv_kernel
        if bias:
            FLOPs += out_channels
        
        # return
        return FLOPs
    
    @staticmethod
    def add(img_size:int|tuple[int, int], img_channels:int):
        img_size = to_2tuple(img_size)
        return int(img_size[0] * img_size[1] * img_channels)

    @staticmethod
    def relu(img_size:int|tuple[int, int], img_channels:int):
        img_size = to_2tuple(img_size)
        return int(img_size[0] * img_size[1] * img_channels)
