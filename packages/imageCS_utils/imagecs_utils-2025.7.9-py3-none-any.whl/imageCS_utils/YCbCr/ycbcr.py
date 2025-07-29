import torch
from torch import Tensor

_rgb2ycbcr_matrix = torch.tensor(
    [[65.481, 128.553, 24.966],
     [-37.797, -74.203, 112.0],
     [112.0, -93.786, -18.214]]
)

_ycbcr2rgb_matrix:Tensor = torch.linalg.inv(_rgb2ycbcr_matrix)

_r2y_00 = _rgb2ycbcr_matrix[0][0].item()
_r2y_01 = _rgb2ycbcr_matrix[0][1].item()
_r2y_02 = _rgb2ycbcr_matrix[0][2].item()
_r2y_10 = _rgb2ycbcr_matrix[1][0].item()
_r2y_11 = _rgb2ycbcr_matrix[1][1].item()
_r2y_12 = _rgb2ycbcr_matrix[1][2].item()
_r2y_20 = _rgb2ycbcr_matrix[2][0].item()
_r2y_21 = _rgb2ycbcr_matrix[2][1].item()
_r2y_22 = _rgb2ycbcr_matrix[2][2].item()

_y2r_00 = _ycbcr2rgb_matrix[0][0].item()
_y2r_01 = _ycbcr2rgb_matrix[0][1].item()
_y2r_02 = _ycbcr2rgb_matrix[0][2].item()
_y2r_10 = _ycbcr2rgb_matrix[1][0].item()
_y2r_11 = _ycbcr2rgb_matrix[1][1].item()
_y2r_12 = _ycbcr2rgb_matrix[1][2].item()
_y2r_20 = _ycbcr2rgb_matrix[2][0].item()
_y2r_21 = _ycbcr2rgb_matrix[2][1].item()
_y2r_22 = _ycbcr2rgb_matrix[2][2].item()

def rgb2ycbcr(RGB_image:Tensor, range=1) -> Tensor:
    """
    ITU-R BT.601 conversion (Digital)
    [ref] https://en.wikipedia.org/wiki/YCbCr

    input_shape: (..., 3, H, W)
    output_shape: (..., 3, H, W)
    """
    assert len(RGB_image.shape) >= 3 and RGB_image.shape[-3] == 3
    assert range in [1, 255]
    
    if range == 255:
        RGB_image = RGB_image / 255.

    R = RGB_image[..., 0, :, :]
    G = RGB_image[..., 1, :, :]
    B = RGB_image[..., 2, :, :]

    Y = _r2y_00 * R + _r2y_01 * G + _r2y_02 * B + 16
    Cb = _r2y_10 * R + _r2y_11 * G + _r2y_12 * B + 128
    Cr = _r2y_20 * R + _r2y_21 * G + _r2y_22 * B + 128

    YCbCr_image = torch.stack([Y, Cb, Cr], dim=-3)

    if range == 1:
        YCbCr_image = YCbCr_image / 255.
    YCbCr_image = YCbCr_image.to(RGB_image.dtype)

    return YCbCr_image

def ycbcr2rgb(YCbCr_image:Tensor, range=1) -> Tensor:
    """
    ITU-R BT.601 conversion (Digital)
    [ref] https://en.wikipedia.org/wiki/YCbCr

    input_shape: (..., 3, H, W)
    output_shape: (..., 3, H, W)
    """
    assert len(YCbCr_image.shape) >= 3 and YCbCr_image.shape[-3] == 3
    assert range in [1, 255]

    if range == 1:
        YCbCr_image = YCbCr_image * 255.
    
    Y = YCbCr_image[..., 0, :, :]
    Cb= YCbCr_image[..., 1, :, :]
    Cr = YCbCr_image[..., 2, :, :]

    Y = Y - 16
    Cb = Cb - 128
    Cr = Cr - 128

    R = _y2r_00 * Y + _y2r_01 * Cb + _y2r_02 * Cr
    G = _y2r_10 * Y + _y2r_11 * Cb + _y2r_12 * Cr
    B = _y2r_20 * Y + _y2r_21 * Cb + _y2r_22 * Cr

    RGB_image = torch.stack([R, G, B], dim=-3)
    if range == 255:
        RGB_image = RGB_image * 255.
    RGB_image = RGB_image.to(YCbCr_image.dtype)

    return RGB_image
    