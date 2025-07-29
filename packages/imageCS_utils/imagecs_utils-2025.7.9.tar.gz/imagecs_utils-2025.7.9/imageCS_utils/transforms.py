"""some custmer torchvision transforms"""
import random
from typing import Sequence
import torchvision.transforms.functional as TF

class RandomRotateFixAngle:
    """
    choose fix angles to random rotate
    https://github.com/pytorch/vision/issues/566#issuecomment-535854734
    """
    def __init__(self, angles: Sequence[int]):
        self.angles = angles

    def __call__(self, x):
        angle = random.choice(self.angles)
        return TF.rotate(x, angle)