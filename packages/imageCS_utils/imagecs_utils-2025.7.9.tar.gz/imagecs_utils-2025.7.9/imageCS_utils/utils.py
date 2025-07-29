"""lots of torch utils and tools"""
import argparse
import pickle
import json
import os
import shutil
from copy import deepcopy, copy
from threading import Thread
import PIL
from typing import Tuple, TypeVar

import torch
from torch import Tensor
from timm.models.layers import to_2tuple as timm_to_2tuple
from einops import rearrange

import torchvision
from torchvision import transforms
from torchvision.transforms.functional import resize as torch_resize

from .base_utils.info import Info
from .get_matrix import get_dft_matrix, get_index_matrix, get_standard_orthogonal_matrix

_T_type = TypeVar("_T_type")

def to_2tuple(x:_T_type|Tuple[_T_type, _T_type]):
    out:Tuple[_T_type, _T_type] = timm_to_2tuple(x)
    return out

class BaseThread:
    """easy way to manage thread"""
    def __init__(self) -> None:
        self.thread_list = []
    
    def add(self, f, *args, **kwargs):
        """add a thread to the pool"""
        thread = Thread(target=f, args=args, kwargs=kwargs)
        self.thread_list.append(thread)
    
    def start(self):
        """start all thread in the pool"""
        for thread in self.thread_list:
            thread.start()
    
    def wait(self):
        """wait all thread finished in the pool"""
        for thread in self.thread_list:
            thread.join()
        self.thread_list.clear()

class PhiFunction:
    @staticmethod
    def _phi_function(inputs:Tensor, phi:Tensor, block_size:int|Tuple[int, int], transpose:bool):
        """
        [ref] Optimization-Inspired Cross-Attention Transformer for Compressive Sensing (CVPR2023, J. Song et al.)
        Modify based on PhiTPhi_fun in https://github.com/songjiechong/OCTUF/blob/main/model_octuf.py

        if transpose == True:
            return PhiT @ inputs
        else:
            return Phi @ inputs
        """
        (block_h, block_w) = to_2tuple(block_size)
        (cs_out, cs_in) = phi.size()
        assert block_h == block_w
        assert block_h * block_w == cs_in
        stride = block_w
        phi_kernel = phi.view(cs_out, 1, block_h, block_w)

        if transpose:
            outputs = torch.conv_transpose2d(inputs, phi_kernel, stride=stride)
        else:
            outputs = torch.conv2d(inputs, phi_kernel, stride=stride)

        return outputs
    
    @staticmethod
    def phi(x:Tensor, phi:Tensor, block_size:int|Tuple[int, int]):
        r"""$\Phi x$ function"""
        return PhiFunction._phi_function(
            inputs=x,
            phi=phi,
            block_size=block_size,
            transpose=False
        )

    @staticmethod
    def phiT(y:Tensor, phi:Tensor, block_size:int|Tuple[int, int]):
        r"""$\Phi^T y$ function"""
        return PhiFunction._phi_function(
            inputs=y,
            phi=phi,
            block_size=block_size,
            transpose=True
        )

    @staticmethod
    def phiTphi(x:Tensor, phi:Tensor, block_size:int|Tuple[int, int]):
        r"""$\Phi^T \Phi x$ function"""
        phix = PhiFunction.phi(x, phi, block_size)
        phiTphix = PhiFunction.phiT(phix, phi, block_size)
        return phiTphix
    
    @staticmethod
    def a(inputs:Tensor, a:Tensor, block_size:int|Tuple[int, int], matmul_type:str):
        r"""
        $A x$ function
        matmal_type = "x" or "y"
        """
        assert matmul_type in ["x", "y"]
        (block_h, block_w) = to_2tuple(block_size)
        (dim1, dim2) = a.size()
        assert block_h == block_w
        assert dim1 == dim2
        dim = dim1

        if matmul_type == "x":
            stride = block_w
            a_kernel = a.view(dim, 1, block_h, block_w)
        elif matmul_type == "y":
            stride = 1
            a_kernel = a.view(dim, dim, 1, 1)

        outputs = torch.conv2d(inputs, a_kernel, stride=stride)
        if matmul_type == "x":
            outputs = torch.pixel_shuffle(outputs, block_w)

        return outputs

class PhiClass:
    def __init__(self, phi:Tensor, block_size:int|Tuple[int, int]):
        self.phi_matrix = phi
        self.block_size = block_size
    
    def phi(self, x:Tensor):
        return PhiFunction.phi(x, self.phi_matrix, self.block_size)
    
    def phiT(self, y:Tensor):
        return PhiFunction.phiT(y, self.phi_matrix, self.block_size)
    
    def phiTphi(self, x:Tensor):
        return PhiFunction.phiTphi(x, self.phi_matrix, self.block_size)

def get_transforms(grayscale:bool, resize=None, gauss:bool=False):
    """get an easy torchvision.transforms"""
    if resize is not None:
        resize = to_2tuple(resize)

    trans = [transforms.ToTensor()]
    if grayscale:
        trans.append(transforms.Grayscale())
    if resize is not None:
        trans.append(transforms.Resize(resize))
    if gauss:
        trans.append(transforms.GaussianBlur((3, 3)))
    
    trans = transforms.Compose(trans)
    return trans

def save_image(image:Tensor, file_name:str, *args, **kwargs):
    torchvision.utils.save_image(image, file_name, *args, **kwargs)

def init_folder_path(*args, overwrite=False):
    """init a folder, is overwrite is True, the folder will be empty first"""
    for path in args:
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            if overwrite:
                shutil.rmtree(path)
                os.makedirs(path)

def check_path_exist(path:str):
    """check if the path exist"""
    return os.path.exists(path)

def dict2namespace(config:dict):
    """dict() to argparse.Namespace()"""
    namespace = argparse.Namespace()
    for key, value in config.items():
        if isinstance(value, dict):
            new_value = dict2namespace(value)
        else:
            new_value = value
        setattr(namespace, key, new_value)
    return namespace

def point2line_vec(point_a:Tensor, point_b:Tensor, point_p:Tensor) -> Tensor:
    """
    get point to line vec
    return vec

    ref: https://softwareengineering.stackexchange.com/a/168577
    given a line through two points A and B, the minimum distance d to a point P can be computed as:
        n_vector pa = p - a
        n_vector ba = b - a
        double t = dot(pa, ba)/dot(ba, ba)
        vec = pa - t * ba
        # double d = length(pa - t * ba)
    """

    assert point_a.shape == point_b.shape == point_p.shape

    vec_ab = point_b - point_a
    vec_ap = point_p - point_a

    t = (vec_ap * vec_ab).sum() / vec_ab.pow(2).sum()

    vec = t * vec_ab - vec_ap
    return vec

def freeze_model_(model:torch.nn.Module):
    """freeze the model params"""
    for param in model.parameters():
        param.requires_grad = False

def get_optimizer_lr(optimizer:torch.optim.Optimizer):
    """get the optimizer learning rate"""
    for param_group in optimizer.param_groups:
        return param_group['lr']

def load_single_image(file_path:str, image_convert='RGB') -> Tensor:
    """load single image via path, return Tensor"""
    x = PIL.Image.open(file_path)
    x = x.convert(image_convert)
    x = torchvision.transforms.ToTensor()(x)
    return x

def save_single_image(image:torch.Tensor, file_path:str):
    """save single image"""
    save_image(image, file_path)

def resize_image(image:torch.Tensor, size:list[int]):
    """resize image size"""
    image = torch_resize(image, size)
    return image

def argv2str(argv_list:list):
    """argv to str"""
    s = ""
    for arg in argv_list:
        s += arg + " "
    return s[:-1]

def get_random_1d_index(total_numel:int):
    """
    get an random 1-dim index
    for example:
        index = [0, 1, 2, 3, 4, 5]
        you may get random_index = [3, 2, 4, 5, 0, 1]
    by using this function, you can get random index
    """
    random_index = torch.randn((total_numel, )).view(-1)
    random_index = torch.argsort(random_index)

    return random_index

class ListSplit:
    """Tool for split list"""
    @staticmethod
    def via_size(lst:list[_T_type], chunk_size:int):
        """
        set chunk size (element numbers) as condition
        """
        lst_len = len(lst)
        assert chunk_size <= lst_len
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    def via_num(lst:list[_T_type], chunk_num:int):
        """
        set chunk numbers as condition
        """
        lst_len = len(lst)
        assert chunk_num <= lst_len

        chunk_size = lst_len // chunk_num
        last_size = lst_len % chunk_num
        if last_size == 0:
            # directly split
            return ListSplit.via_size(lst, chunk_size)
        elif last_size > chunk_size / 2:
            # divide the extra elements equally
            return ListSplit.via_size(lst, chunk_size+1)
        else:
            # combine last two chuck
            l = ListSplit.via_size(lst, chunk_size)
            chunk1 = l.pop()
            chunk2 = l.pop()
            l.append(chunk1 + chunk2)
            return l



class ModelTools:
    """freeze and unfrezz model params easy tool"""
    @staticmethod
    def freeze_(model:torch.nn.Module):
        """freeze model params tool"""
        for param in model.parameters():
            param.requires_grad = False

    @staticmethod
    def unfreeze_(model:torch.nn.Module):
        """unfreeze model params tool"""
        for param in model.parameters():
            param.requires_grad = True

class PickleIO:
    """save and load pkl file easy tool"""
    @staticmethod
    def save(data, file_path:str):
        """easy way to save pkl file"""
        with open(file_path, "wb") as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(file_path:str):
        """easy way to load pkl file"""
        with open(file_path, "rb")as f:
            i = pickle.load(f)
        return i

class JsonIO:
    """save and load json file easy tool"""
    @staticmethod
    def save(data:str, file_path:str):
        """easy way to save json file"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    @staticmethod
    def load(file_path:str):
        """easy way to load json file"""
        with open(file_path, "r", encoding="utf-8")as f:
            i = json.load(f)
        return i
    
class DictOperation:
    """easy way to handle dict"""
    @staticmethod
    def merge_(a: dict, b: dict) -> dict:
        """
        merge dict from b to a
        MIT license
        Copyright tfeldmann from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
        """
        result = deepcopy(a)
        for bk, bv in b.items():
            av = result.get(bk)
            if isinstance(av, dict) and isinstance(bv, dict):
                result[bk] = DictOperation.merge_(av, bv)
            else:
                result[bk] = deepcopy(bv)
        return result
    
class ImageEmbedding:
    """
    easy way to padding zeros and embedding image and makes
    the image's width and height divisible by the width and
    height of the block when divided into blocks.
    """
    @staticmethod
    def _side_padding(padding_h:int, padding_w:int, padding_type:str):
        assert padding_type in ["one_side", "two_side"]
        if padding_type == "one_side":
            padding_top = int(0)
            padding_bottom = padding_h
            padding_left = int(0)
            padding_right = padding_w
            return (padding_left, padding_top, padding_right, padding_bottom)
        elif padding_type == "two_side":
            padding_top = padding_h // 2
            padding_bottom = padding_h - padding_top
            padding_left = padding_w // 2
            padding_right = padding_w - padding_left
            return (padding_left, padding_top, padding_right, padding_bottom)
        else:
            raise RuntimeError()

    @staticmethod
    def _get_padding(image_size:Tuple[int, int], patch_size:Tuple[int, int], padding_type="one_side"):
        assert padding_type in ["one_side", "two_side"]
        (img_h, img_w) = image_size
        (patch_h, patch_w) = patch_size

        padding_h = img_h % patch_h
        padding_w = img_w % patch_w
        if padding_h != 0:
            padding_h = patch_h - padding_h
        if padding_w != 0:
            padding_w = patch_w - padding_w
        
        return ImageEmbedding._side_padding(padding_h, padding_w, padding_type)

    @staticmethod
    def _get_overlap_padding(image_size:Tuple[int, int], patch_size:Tuple[int, int], overlap_size:int, padding_type="one_side"):
        assert padding_type in ["one_side", "two_side"]
        (img_h, img_w) = image_size

        (patch_h, patch_w) = patch_size
        fake_img_size = (img_h - 2*overlap_size, img_w - 2*overlap_size)
        kernel_size = (patch_h - 2*overlap_size, patch_w - 2*overlap_size)

        return ImageEmbedding._get_padding(fake_img_size, kernel_size, padding_type)

    @staticmethod
    def _padding(image:Tensor, left:int, top:int, right:int, bottom:int, **kwargs):
        image = transforms.Pad((left, top, right, bottom), **kwargs)(image)
        return image
    
    @staticmethod
    def image_auto_padding(image:Tensor, patch_size:int|Tuple[int, int], padding_type="one_side", padding_mode="constant") -> Tensor:
        """
        auto padding image and makes the image's width and height divisible by the width and
        height of the block when divided into blocks.
        """
        assert padding_type in ["one_side", "two_side"]
        image_size:Tuple[int, int] = image.size()[-2:]
        patch_size = to_2tuple(patch_size)
        (padding_left, padding_top, padding_right, padding_bottom) = ImageEmbedding._get_padding(image_size, patch_size, padding_type)
        
        if not padding_left == padding_right == padding_top == padding_bottom == 0:
            image = ImageEmbedding._padding(image, padding_left, padding_top, padding_right, padding_bottom, padding_mode=padding_mode)
        
        return image

    @staticmethod
    def image_auto_unpadding(image:Tensor, orgin_image_size:int|Tuple[int, int], patch_size:int|Tuple[int, int], padding_type="one_side") -> Tensor:
        """The inverse function of image_auto_padding()"""
        assert padding_type in ["one_side", "two_side"]
        image_size = to_2tuple(orgin_image_size)
        patch_size = to_2tuple(patch_size)
        (padding_left, padding_top, padding_right, padding_bottom) = ImageEmbedding._get_padding(image_size, patch_size, padding_type)

        image = image[:, :, padding_top:, padding_left:]
        if padding_bottom != 0:
            image = image[:, :, :-padding_bottom, :]
        if padding_right != 0:
            image = image[:, :, :, :-padding_right]
        
        return image

    @staticmethod
    def image2patches(image:Tensor, patch_size:int|Tuple[int, int], padding_type="one_side", embed_patch=True) -> Tensor:
        """
        Automatically pad zeros and divide each small block into the batch_size dimension.
        If embed_patch is True, the image will also be flattened into vectors.
        """
        (patch_h, patch_w) = patch_size = to_2tuple(patch_size)
        image = ImageEmbedding.image_auto_padding(image, patch_size, padding_type)
        
        if embed_patch:
            patches = rearrange(image, 'b c (nH H) (nW W d) -> (b nH nW) c (H W) d', H=patch_h, W=patch_w, d=1)
        else:
            patches = rearrange(image, 'b c (nH H) (nW W) -> (b nH nW) c H W', H=patch_h, W=patch_w)

        return patches
    
    @staticmethod
    def patches2image(patches:Tensor, orgin_image_size:int|Tuple[int, int], patch_size:int|Tuple[int, int], padding_type="one_side", embed_patch=True) -> Tensor:
        """The inverse function of image2patches()"""
        assert padding_type in ["one_side", "two_side"]
        (image_h, image_w) = image_size = to_2tuple(orgin_image_size)
        (patch_h, patch_w) = patch_size = to_2tuple(patch_size)
        (padding_left, padding_top, padding_right, padding_bottom) = ImageEmbedding._get_padding(image_size, patch_size, padding_type)
        (h, w) = (image_h+padding_top+padding_bottom, image_w+padding_left+padding_right)
        (num_patch_h, num_patch_w) = (h//patch_h, w//patch_w)

        if embed_patch:
            image = rearrange(patches, '(b nH nW) c (H W) d -> b c (nH H) (nW W d)', nH=num_patch_h, nW=num_patch_w, H=patch_h, W=patch_w)
        else:
            image = rearrange(patches, '(b nH nW) c H W -> b c (nH H) (nW W)', nH=num_patch_h, nW=num_patch_w, H=patch_h, W=patch_w)

        image = ImageEmbedding.image_auto_unpadding(image, orgin_image_size, patch_size, padding_type)

        return image

    @staticmethod
    def overlap_image2patches(image:Tensor, patch_size:Tuple[int, int], overlap_size:int, padding_mode="constant") -> Tensor:
        """
        Similar to the image2patches() function, but there will be overlapping areas when divided into blocks.

        patch_size: the size of patches height and width
        overlap_size: 

        os: overlap_size
        ks: kernel_size

                    [os os os]
        patches =   [os ks os]
                    [os os os]

        """
        image = ImageEmbedding._padding(image, overlap_size, overlap_size, overlap_size, overlap_size)
        (patch_h, patch_w) = patch_size

        image_size = image.shape[-2:]
        (padding_left, padding_top, padding_right, padding_bottom) = ImageEmbedding._get_overlap_padding(image_size, patch_size, overlap_size, "one_side")
        image = ImageEmbedding._padding(image, padding_left, padding_top, padding_right, padding_bottom, padding_mode=padding_mode)

        (image_h, image_w) = image.shape[-2:]
        patches = []

        (stride_h, stride_w) = (patch_h - 2*overlap_size, patch_w - 2*overlap_size)

        h = 0
        while True:
            h_start_idx = h * stride_h
            h_end_idx = h_start_idx + patch_h

            w = 0
            while True:
                w_start_idx = w * stride_w
                w_end_idx = w_start_idx + patch_w


                patches.append(image[:, :, h_start_idx:h_end_idx, w_start_idx:w_end_idx])

                assert w_end_idx <= image_w
                if w_end_idx == image_w:
                    break
                w += 1

            assert h_end_idx <= image_h
            if h_end_idx == image_h:
                break
            h += 1
        
        patches = torch.stack(patches, dim=0)
        patches = rearrange(patches, 'n b c H W -> (b n) c (H W)')
        patches = patches.unsqueeze(-1)
        return patches

    @staticmethod
    def overlap_patches2image(patches:Tensor, orgin_image_size:Tuple[int, ...], patch_size:Tuple[int, int], overlap_size:int) -> Tensor:
        """The inverse function of overlap_image2patches()"""
        (image_h, image_w) = orgin_image_size[-2:]
        (patch_h, patch_w) = patch_size

        (image_overlap_fix_h, image_overlap_fix_w) = image_overlap_fix_size = (image_h + 2*overlap_size, image_w + 2*overlap_size)
        (_, _, padding_right, padding_bottom) = ImageEmbedding._get_overlap_padding(image_overlap_fix_size, patch_size, overlap_size, "one_side")
        (h, w) = (image_overlap_fix_h + padding_bottom, image_overlap_fix_w + padding_right)
        (num_patch_h, num_patch_w) = ((h-2*overlap_size) // (patch_h-2*overlap_size), (w-2*overlap_size) // (patch_w-2*overlap_size))

        patches = patches.squeeze(-1)
        patches = rearrange(patches, '(b nH nW) c (H W) -> b nH nW c H W', nH=num_patch_h, nW=num_patch_w, H=patch_h, W=patch_w)
        (batch_size, _, _, c, _, _) = patches.shape

        image = torch.empty((batch_size, c, h, w), device=patches.device, dtype=patches.dtype)

        (stride_h, stride_w) = (patch_h - 2*overlap_size, patch_w - 2*overlap_size)

        h = 0
        while True:
            h_start_idx = h * stride_h
            h_end_idx = h_start_idx + patch_h

            w = 0
            while True:
                w_start_idx = w * stride_w
                w_end_idx = w_start_idx + patch_w

                (h1, h2) = (h_start_idx + overlap_size, h_end_idx - overlap_size)
                (w1, w2) = (w_start_idx + overlap_size, w_end_idx - overlap_size)
                if overlap_size == 0:
                    image[:, :, h1:h2, w1:w2] = patches[:, h, w, :, :, :]
                else:
                    image[:, :, h1:h2, w1:w2] = patches[:, h, w, :, overlap_size:-overlap_size, overlap_size:-overlap_size]

                assert w_end_idx <= w
                if w_end_idx == w:
                    break
                w += 1

            assert h_end_idx <= w
            if h_end_idx == w:
                break
            h += 1
        
        if padding_bottom != 0:
            image = image[:, :, :-padding_bottom, :]
        if padding_right != 0:
            image = image[:, :, :, :-padding_right]
        if overlap_size != 0:
            image = image[:, :, overlap_size:-overlap_size, overlap_size:-overlap_size]
        return image
 

class ConvMatrix:
    """Convert conv function to an left matrix"""
    @staticmethod
    def _index2d_to_index1d(index2d, image_size):
        (idx_h, idx_w) = index2d
        (img_h, img_w) = to_2tuple(image_size)
        assert idx_h < img_h and idx_w < img_w

        index1d = idx_h * img_w + idx_w
        return index1d
    
    @staticmethod
    def _judge_index_state(idx, img_size, padding):
        if 0 <= idx < img_size:
            return "img"
        elif idx >= -padding or idx < img_size + padding:
            return "pad"
        else:
            return "out"
    
    @staticmethod
    def _index_kernel2orgin_map(target_index, orgin_image_size, kernel_size, stride, padding, padding_mode="zeros"):
        assert padding_mode in ["zeros"]
        (target_idx_h, target_idx_w) = to_2tuple(target_index)
        (img_h, img_w) = to_2tuple(orgin_image_size)
        (kernel_h, kernel_w) = to_2tuple(kernel_size)
        (stride_h, stride_w) = to_2tuple(stride)
        (padding_h, padding_w) = to_2tuple(padding)

        idx_dict = dict()
        for kernel_ptr_h in range(kernel_h):
            for kernel_ptr_w in range(kernel_w):
                # init
                ignore_idx = False
                # Get ptr_h
                ptr_h = target_idx_h * stride_h + kernel_ptr_h - padding_h
                ptr_h_state = ConvMatrix._judge_index_state(ptr_h, img_h, padding_h)
                if ptr_h_state == "pad":
                    ignore_idx = True
                elif ptr_h_state == "out":
                    raise RuntimeError()

                # Get ptr_w
                ptr_w = target_idx_w * stride_w + kernel_ptr_w - padding_w
                ptr_w_state = ConvMatrix._judge_index_state(ptr_w, img_w, padding_w)
                if ptr_w_state == "pad":
                    ignore_idx = True
                elif ptr_w_state == "out":
                    raise RuntimeError()
                
                if not ignore_idx:
                    idx_dict[(kernel_ptr_h, kernel_ptr_w)] = (ptr_h, ptr_w)
        
        return idx_dict
    
    @staticmethod
    def _get_target_image_size(orgin_image_size, kernel_size, stride, padding):
        (img_h, img_w) = to_2tuple(orgin_image_size)
        (kernel_h, kernel_w) = to_2tuple(kernel_size)
        (stride_h, stride_w) = to_2tuple(stride)
        (padding_h, padding_w) = to_2tuple(padding)

        target_h = (img_h + 2 * padding_h - (kernel_h - 1) - 1) // stride_h + 1
        target_w = (img_w + 2 * padding_w - (kernel_w - 1) - 1) // stride_w + 1

        return (target_h, target_w)

    @staticmethod
    def _get_target2orgin_maps(img_size, kernel_size, stride, padding, padding_mode="zeros"):
        (target_h, target_w) = ConvMatrix._get_target_image_size(
            orgin_image_size=img_size,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding
        )

        target2orgin_dict = dict()
        # Get idx_dict
        def _parallel_get_index_target2orgin_map(target2orgin_dict, target_h_ptr, target_w, orgin_image_size, kernel_size, stride, padding, padding_mode="zeros"):
            for target_w_ptr in range(target_w):
                kernel2orgin_map_dict = ConvMatrix._index_kernel2orgin_map(
                    target_index=(target_h_ptr, target_w_ptr),
                    orgin_image_size=orgin_image_size,
                    kernel_size=kernel_size,
                    stride=stride,
                    padding=padding,
                    padding_mode=padding_mode,
                )
                target_ptr = (target_h_ptr, target_w_ptr)
                target2orgin_dict[target_ptr] = kernel2orgin_map_dict

        parallel = BaseThread()
        for target_h_ptr in range(target_h):
            parallel.add(
                _parallel_get_index_target2orgin_map,
                target2orgin_dict=target2orgin_dict,
                target_h_ptr= copy(target_h_ptr),
                target_w=target_w,
                orgin_image_size=img_size,
                kernel_size=kernel_size,
                stride=stride,
                padding=padding,
                padding_mode=padding_mode,
            )
        parallel.start()
        Info.info("Getting Target2Orgin Map")
        parallel.wait()

        return target2orgin_dict

    @staticmethod
    def _get_index_data(target2orgin_dict, kernel, image_size, target_size):
        # (out_dim, in_dim, *kernel_size)
        (out_dim, in_dim, *_) = kernel.size()

        def _parallel_get_index_data(index_data_list, target_ptr_1d, kernel2orgin_dict):
            for kernel_ptr in kernel2orgin_dict:
                (kernel_ptr_h, kernel_ptr_w) = kernel_ptr
                img_ptr = kernel2orgin_dict[kernel_ptr]

                img_ptr_1d = ConvMatrix._index2d_to_index1d(img_ptr, image_size)

                for out_dim_ptr in range(out_dim):
                    for in_dim_ptr in range(in_dim):
                        matrix_ptr_h = target_ptr_1d * out_dim + out_dim_ptr
                        matrix_ptr_w = img_ptr_1d * in_dim + in_dim_ptr
                        matrix_value = kernel[out_dim_ptr, in_dim_ptr, kernel_ptr_h, kernel_ptr_w]

                        index_data = [matrix_ptr_h, matrix_ptr_w, matrix_value]
                        index_data_list.append(index_data)

        index_data_list = list()
        parallel = BaseThread()
        for target_ptr in target2orgin_dict:
            kernel2orgin_dict = target2orgin_dict[target_ptr]
            target_ptr_1d = ConvMatrix._index2d_to_index1d(target_ptr, target_size)

            parallel.add(
                _parallel_get_index_data,
                index_data_list=index_data_list,
                target_ptr_1d=copy(target_ptr_1d),
                kernel2orgin_dict=kernel2orgin_dict
            )
        parallel.start()
        Info.info("Getting Index Data")
        parallel.wait()

        index_data_list = torch.tensor(index_data_list)
        
        index_data_list = index_data_list.T
        indices = index_data_list[0:2].to(torch.long)
        values = index_data_list[2]

        return (indices, values)
    
    @staticmethod
    def get_conv_matrix(orgin_image_size, kernel, stride, padding, padding_mode="zeros"):
        """Regard conv function as an left matrix and return this matrix"""
        (out_dim, in_dim, *kernel_size) = kernel.size()
        (img_h, img_w) = to_2tuple(orgin_image_size)

        (target_h, target_w) = target_size = ConvMatrix._get_target_image_size(
            orgin_image_size=orgin_image_size,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding
        )

        matrix_size = (target_h*target_w*out_dim, img_h*img_w*in_dim)


        target2orgin_dict = ConvMatrix._get_target2orgin_maps(
            img_size=orgin_image_size,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            padding_mode=padding_mode
        )

        (indices, values) = ConvMatrix._get_index_data(
            target2orgin_dict=target2orgin_dict,
            kernel=kernel,
            image_size=orgin_image_size,
            target_size=target_size
        )

        sparse_matrix = torch.sparse_coo_tensor(
            indices=indices,
            values=values,
            size=matrix_size
        )

        return sparse_matrix

    @staticmethod
    def conv(conv_matrix, img, kernel_size, stride, padding):
        """using left matrix to achieve conv function"""
        # (B, C, H, W)
        (_, _, img_h, img_w) = img.size()
        (target_h, target_w) = ConvMatrix._get_target_image_size(
            orgin_image_size=(img_h, img_w),
            kernel_size=kernel_size,
            stride=stride,
            padding=padding
        )

        img = rearrange(img, "B C H W -> (H W C) B")
        img = conv_matrix @ img
        img = rearrange(img, "(H W C) B -> B C H W", H=target_h, W=target_w)

        return img

    @staticmethod
    def mm(conv_matrix, img, target_size):
        """same as self.conv() function, but you can specify output size"""
        (target_h, target_w) = to_2tuple(target_size)

        img = rearrange(img, "B C H W -> (H W C) B")
        img = conv_matrix @ img
        img = rearrange(img, "(H W C) B -> B C H W", H=target_h, W=target_w)

        return img
