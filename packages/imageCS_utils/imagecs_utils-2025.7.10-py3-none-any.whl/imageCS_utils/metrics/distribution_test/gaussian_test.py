import torch
from torch import Tensor
import torch
import numpy as np
from scipy.stats import anderson

def anderson_darling_test(data:Tensor, with_batch=False):
    # [ref] https://www.geeksforgeeks.org/how-to-perform-an-anderson-darling-test-in-python/
    if with_batch:
        bs = data.size(0)
        data_list = [data[idx].detach().cpu().view(-1).numpy() for idx in range(bs)]
    else:
        data_list = [data.detach().cpu().view(-1).numpy()]
    
    ans_list = list()
    for data in data_list:
        result = anderson(data)
        statistic = result.statistic
        critical_values = result.critical_values
        significance_levels = result.significance_level

        is_gaussian = False
        for (critical_value, significance_level) in zip(critical_values, significance_levels):
            if statistic <= critical_value:
                is_gaussian = True
                break
        
        if is_gaussian:
            ans = dict(
                is_gaussian = True,
                mean = np.mean(data),
                var = np.var(data),
                significance_level = significance_level,
            )
        else:
            ans = dict(
                is_gaussian = False,
                mean = np.mean(data),
                var = np.var(data),
                significance_level = 0.0
            )
        
        ans_list.append(ans)
    
    return ans_list

