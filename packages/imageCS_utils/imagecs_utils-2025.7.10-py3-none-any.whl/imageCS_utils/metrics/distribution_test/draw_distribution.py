import torch
from torch import Tensor
import torch
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def draw_distribution(data:Tensor, bins_num:int, save_path:str, color='lightgreen', ec='black'):
    data = data.detach().cpu().view(-1).numpy()
    (fig, ax) = plt.subplots()
    ax.hist(data, bins_num, color=color, ec=ec)
    fig.savefig(save_path)
    
def draw_qq_plot(data:Tensor, save_path:str, dist="norm"):
    data = data.detach().cpu().view(-1).numpy()
    (fig, ax) = plt.subplots()
    stats.probplot(data, dist=dist, plot=ax)
    fig.savefig(save_path)
