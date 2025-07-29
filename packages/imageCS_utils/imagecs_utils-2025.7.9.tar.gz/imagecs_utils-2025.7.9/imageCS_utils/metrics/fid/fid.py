from typing import Iterable
import torch
from torch import Tensor
from torch.nn.functional import adaptive_avg_pool2d
from pytorch_fid.inception import InceptionV3

def get_inception_model(dims=2048):
    """
    Inspired by: https://github.com/mseitzer/pytorch-fid/src/pytorch_fid/fid_score.py
    """
    block_idx = InceptionV3.BLOCK_INDEX_BY_DIM[dims]
    return InceptionV3([block_idx])

def get_activations(model:torch.nn.Module, batches:Iterable[Tensor], device:torch.device):
    """
    Inspired by: https://github.com/mseitzer/pytorch-fid/src/pytorch_fid/fid_score.py
    """
    with torch.no_grad():
        model = model.eval()
        activations:list[Tensor] = []

        for batch in batches:
            batch = batch.to(device)
            pred = model(batch)[0]
            if pred.size(2) != 1 or pred.size(3) != 1:
                pred = adaptive_avg_pool2d(pred, output_size=(1, 1))
            activations.append(pred.cpu().data.reshape(pred.size(0), -1))
    
    return torch.cat(activations, dim=0)

def calculate_activation_statistics(activations:Tensor):
    """
    Inspired by: https://github.com/mseitzer/pytorch-fid/src/pytorch_fid/fid_score.py
    """
    mu = activations.mean(dim=0)
    sigma = activations.t().cov()
    return mu, sigma

def frechet_distance(mu_x:Tensor, sigma_x:Tensor, mu_y:Tensor, sigma_y:Tensor) -> Tensor:
    """
    Inspired by: https://www.reddit.com/r/MachineLearning/comments/12hv2u6/d_a_better_way_to_compute_the_fr%C3%A9chet_inception/
    Issues: https://github.com/mseitzer/pytorch-fid/issues/95
    """
    a = (mu_x - mu_y).square().sum(dim=-1)
    b = sigma_x.trace() + sigma_y.trace()
    c = torch.linalg.eigvals(sigma_x @ sigma_y).sqrt().real.sum(dim=-1)

    return a + b - 2 * c

class FID:
    def __init__(
            self,
            model=get_inception_model(),
            device=torch.device("cpu"),
            get_activations_func=get_activations
        ):
        self.model = model.to(device)
        self.dev = device
        self.get_activations = get_activations_func
    
    def fid(self, batches1:Iterable[Tensor], batches2:Iterable[Tensor], *args, **kwargs):
        act1 = self.get_activations(self.model, batches1, self.dev, *args, **kwargs)
        mu1, sigma1 = calculate_activation_statistics(act1)

        act2 = self.get_activations(self.model, batches2, self.dev, *args, **kwargs)
        mu2, sigma2 = calculate_activation_statistics(act2)

        fid_value = frechet_distance(mu1, sigma1, mu2, sigma2)
        fid_value[fid_value<0] = 0

        return fid_value
