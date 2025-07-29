"""Used for automatic image segmentation and automatic padding."""

from .utils import ImageEmbedding
from torch import Tensor

class _AutoImage_Abstract:
    def __init__(self, img:Tensor, patch_size:int|tuple[int, int], padding_type="one_side"):
        assert len(img.size()) == 4
        (img_batch_size, img_channels, img_h, img_w) = img.size()

        self._patch_size = patch_size
        self._padding_type = padding_type

        self._bs = img_batch_size
        self._ch = img_channels
        self._imh = img_h
        self._imw = img_w
    
    def encode(self, img:Tensor):
        raise NotImplementedError

    def decode(self, enc_img:Tensor):
        raise NotImplementedError

class AutoImageEmbedding(_AutoImage_Abstract):
    def __init__(self, img: Tensor, patch_size: int | tuple[int, int], padding_type="one_side"):
        super().__init__(img, patch_size, padding_type)

    def encode(self, img:Tensor):
        patches = ImageEmbedding.image2patches(
            image = img,
            patch_size = self._patch_size,
            padding_type = self._padding_type,
            embed_patch = True
        )
        return patches
    
    def decode(self, patches:Tensor):
        img = ImageEmbedding.patches2image(
            patches = patches,
            orgin_image_size = (self._imh, self._imw),
            patch_size = self._patch_size,
            padding_type = self._padding_type,
            embed_patch = True
        )
        return img

class AutoImagePatches(_AutoImage_Abstract):
    def __init__(self, img: Tensor, patch_size: int | tuple[int, int], padding_type="one_side"):
        super().__init__(img, patch_size, padding_type)

    def encode(self, img:Tensor):
        patches = ImageEmbedding.image2patches(
            image = img,
            patch_size = self._patch_size,
            padding_type = self._padding_type,
            embed_patch = False
        )
        return patches
    
    def decode(self, patches:Tensor):
        img = ImageEmbedding.patches2image(
            patches = patches,
            orgin_image_size = (self._imh, self._imw),
            patch_size = self._patch_size,
            padding_type = self._padding_type,
            embed_patch = False
        )
        return img

class AutoImagePadding(_AutoImage_Abstract):
    def __init__(self, img: Tensor, patch_size: int | tuple[int, int], padding_type="one_side", padding_mode="constant"):
        super().__init__(img, patch_size, padding_type)
        self._padding_mode = padding_mode

    def encode(self, img:Tensor):
        image = ImageEmbedding.image_auto_padding(
            image = img,
            patch_size = self._patch_size,
            padding_type = self._padding_type,
            padding_mode = self._padding_mode
        )
        return image
    
    def decode(self, image:Tensor):
        img = ImageEmbedding.image_auto_unpadding(
            image = image,
            orgin_image_size = (self._imh, self._imw),
            patch_size = self._patch_size,
            padding_type = self._padding_type,
        )
        return img
