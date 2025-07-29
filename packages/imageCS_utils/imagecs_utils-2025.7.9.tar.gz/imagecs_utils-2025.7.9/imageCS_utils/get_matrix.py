"""get many kinds of matrix"""
from math import sin, cos, pi
import torch

def get_index_matrix(h, w):
    """
    x.shape = [2, h, w], x[0, ...] is h index, x[1, ...] is w index
    """

    h_index = torch.arange(0, h, 1.0)
    h_index = h_index.repeat(w, 1).T

    w_index = torch.arange(0, w, 1.0)
    w_index = w_index.repeat(h, 1)

    x = torch.stack([h_index, w_index], dim=0)
    return x

def get_standard_orthogonal_matrix(out_dim, in_dim) -> torch.Tensor:
    """using svd to get random orthogonal matrix, return Tensor size = (out_dim, in_dim)"""
    matrix = torch.rand(out_dim, in_dim)
    (u, _, vh) = torch.linalg.svd(matrix, full_matrices=False)
    matrix = u @ vh
    return matrix

def get_standard_orthogonal_matrix_torch_init(out_dim, in_dim) -> torch.Tensor:
    """using torch init to get random orthogonal matrix, return Tensor size = (out_dim, in_dim)"""
    matrix = torch.empty((out_dim, in_dim), dtype=torch.float32)
    matrix = torch.nn.init.orthogonal_(matrix)

    return matrix

def get_xavier_normal_matrix(out_dim:int, in_dim:int) -> torch.Tensor:
    """ using torch.nn.init.xavier_normal to init an random matrix """
    matrix = torch.empty(out_dim, in_dim)
    matrix = torch.nn.init.xavier_normal_(matrix)
    return matrix

def get_dft_matrix(img_h, img_w):
    """
    DFT Matrix = [W_N^(i//N*j//N + i%N*j%N)]
    Shape of DFT Matrix is (K, K)
    """
    assert img_h == img_w

    n = img_h
    k = n * n

    x = get_index_matrix(k, k)
    x = torch.div(x[0], n, rounding_mode='trunc') * torch.div(x[1], n, rounding_mode='trunc') + (x[0] % n) * (x[1] % n)
    x = torch.exp(-1j * 2 * torch.pi * x / n)

    return x

def get_2dim_rotate_matrix(total_dim, dim1, dim2, theta):
    """get 2-dim raotate matrix"""
    theta = pi * theta / 180
    m = torch.eye(total_dim, dtype=torch.float32)
    m[dim1, dim1] = cos(theta)
    m[dim2, dim2] = cos(theta)
    m[dim1, dim2] = sin(theta)
    m[dim2, dim1] = -sin(theta)
    return m

def get_ndim_rotate_matrix(total_dim, dim_list, theta_list, show_process=False):
    """get 2-dim raotate matrix"""
    assert len(dim_list) == len(theta_list)

    m = torch.eye(total_dim, dtype=torch.float32)
    for i, (dim, theta) in enumerate(zip(dim_list, theta_list)):
        if show_process:
            print(f"Getting {total_dim}-Dim Rotate Matrix ({i+1}/{total_dim})")
        (dim1, dim2) = dim
        m_ = get_2dim_rotate_matrix(total_dim, dim1, dim2, theta)
        m = m_ @ m
    
    return m
