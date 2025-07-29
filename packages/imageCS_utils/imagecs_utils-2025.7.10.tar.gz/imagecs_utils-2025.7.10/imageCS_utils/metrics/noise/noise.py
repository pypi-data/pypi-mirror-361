import torch
from torch import Tensor
import types
import os
from utils.utils import init_folder_path
from typing import Dict, List
from ...base_utils.base import MetricsBase as BaseClass
from ...base_utils.trainer import UniversalMetricsTrainer

def get_image_snr(orignal_image:Tensor, noisy_image:Tensor=None, noise:Tensor=None):
    assert (noisy_image == None and noise != None) or (noisy_image != None and noise == None)
    image_size = orignal_image.size()
    assert len(image_size) == 3

    if noisy_image != None:
        assert noisy_image.size() == image_size
        noise = orignal_image - noisy_image
    elif noise != None:
        assert noise.size() == image_size
    
    image_mean = orignal_image.mean()
    noise_var = noise.var()

    snr = 20 * (image_mean / noise_var).log10()
    snr = snr.item()

    return snr

def get_noise_var_via_snr(orignal_image:Tensor, snr:float):
    image_mean = orignal_image.mean()
    var = image_mean / (10**(snr / 20))

    return var.item()

class Noise_Sensitivity_Tester:
    def __init__(self, base:BaseClass, change_method, noise_var=None, snr=None, *change_method_args, **change_method_kwargs):
        assert (noise_var == None and snr != None) or (noise_var != None and snr == None)
        if noise_var != None:
            self.w = noise_var ** 0.5
            self.mode = "Var"
        elif snr != None:
            self.snr = snr
            self.mode = "SNR"
        
        self.base = base
        self._change_test_way(self.base, change_method=change_method, *change_method_args, **change_method_kwargs)
    
    def _get_universal_metrics_trainer_net_forward(self, image_keys_in_data_prepare):
        def _net_forward(trainer_self:UniversalMetricsTrainer, data_prepare_output):
            assert hasattr(trainer_self, '_test_noise_noisy_image_list'), f"Please init list for test noise sensitivity"
            # Change Universal_Metrics_Trainer _net_forward() method
            net_kwargs = dict()
            for net_kwargs_key in trainer_self.net_kwargs_map:
                data_prepare_output_key = trainer_self.net_kwargs_map[net_kwargs_key]
                net_kwargs[net_kwargs_key] = data_prepare_output[data_prepare_output_key]
                # >>> add noise here
                if data_prepare_output_key == image_keys_in_data_prepare:
                    image = data_prepare_output[data_prepare_output_key]
                    image_size = image.size()
                    assert len(image_size) == 4 and image_size[1] == 1
                    if self.mode == "Var":
                        w = self.w
                    elif self.mode == "SNR":
                        var = get_noise_var_via_snr(image, snr=self.snr)
                        w = var**0.5
                    
                    noisy_image = image + w * torch.randn_like(image)
                    net_kwargs[net_kwargs_key] = noisy_image
                    trainer_self._test_noise_noisy_image_list.append(dict(image=image.cpu(), noisy_image=noisy_image.cpu()))
                # <<< add noise here
        
            if trainer_self.time_statistic_flag:
                trainer_self.time_statistic.start()

            net_output = trainer_self.net(**net_kwargs)

            if trainer_self.time_statistic_flag:
                trainer_self.time_statistic.stop()

            if type(net_output) in [tuple, list]:
                net_forward_output = dict()
                for (idx, key) in enumerate(trainer_self.net_forward_output_keys):
                    net_forward_output[key] = net_output[idx]
            else:
                assert len(trainer_self.net_forward_output_keys) == 1
                net_forward_output = dict()
                key = trainer_self.net_forward_output_keys[0]
                net_forward_output[key] = net_output

            return net_forward_output
        
        return _net_forward
    
    def _change_test_way(self, base, change_method, *change_method_args, **change_method_kwargs):
        if change_method in ["universal_metrics_trainer_net_forward"]:
            if change_method == "universal_metrics_trainer_net_forward":
                _net_forward = self._get_universal_metrics_trainer_net_forward(*change_method_args, **change_method_kwargs)
        else:
            _net_forward = change_method(*change_method_args, **change_method_kwargs)

        base.trainer._net_forward = types.MethodType(_net_forward, base.trainer)
    
    def _feed(self, dataloader):
        self.base.trainer._test_noise_noisy_image_list = []
        metrics_func_dict = self.base.cfg["train_config"]["metrics_func_dict"]
        (avg_loss, avg_metrics_dict, avg_time, loss_list, metrics_dict_list, data_prepare_out_list, net_forward_output_list) = self.base.test(dataloader, metrics_func_dict)
        noisy_image_list = self.base.trainer._test_noise_noisy_image_list
        for key in net_forward_output_list:
            try:
                net_forward_output_list[key] = net_forward_output_list[key].cpu()
            except:
                pass

        return (avg_metrics_dict, metrics_dict_list, net_forward_output_list, noisy_image_list)
    
    def test(self):
        test_ans_dict = dict()
        for dataset_name in self.base.dataloader_test_dict:
            dataloader = self.base.dataloader_test_dict[dataset_name]
            test_ans_dict[dataset_name] = self._feed(dataloader)
        
        return test_ans_dict

class Noise_Sensitivity_Tester_for_Universal_Metrics_Trainer(Noise_Sensitivity_Tester):
    def __init__(self, base:BaseClass, image_keys_in_data_prepare, noise_var=None, snr=None):
        super().__init__(base, noise_var=noise_var, snr=snr, change_method="universal_metrics_trainer_net_forward", image_keys_in_data_prepare=image_keys_in_data_prepare)

class Noise_Sensitivity_Tester_Proc:
    def __init__(self, gpu_num:int, noise_var=None, snr=None, Noise_Sensitivity_Tester_class=Noise_Sensitivity_Tester, *default_class_args, **default_class_kwargs):
        self.noise_var = noise_var
        self.snr = snr
        self.Noise_Sensitivity_Tester_class = Noise_Sensitivity_Tester_class
        self.default_class_args = default_class_args
        self.default_class_kwargs = default_class_kwargs

        self.noise_sensitivity_tester_dict:Dict[str, Noise_Sensitivity_Tester] = dict()
        self.all_test_ans_dict = None

        self.gpu_num = gpu_num
        if gpu_num >= 0:
            self.gpu_dev = torch.device("cuda:0")
            os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
            os.environ["CUDA_VISIBLE_DEVICES"] = str(self.gpu_num)
        else:
            self.gpu_dev = torch.device("cpu")
        self.cpu_dev = torch.device("cpu")
    
    def add_model(self, base, model_name, *class_args, **class_kwargs):
        class_args = self.default_class_args + class_args
        class_kwargs = self.default_class_kwargs | class_kwargs

        noise_sensitivity_tester = self.Noise_Sensitivity_Tester_class(base=base, noise_var=self.noise_var, snr=self.snr, *class_args, **class_kwargs)
        self.noise_sensitivity_tester_dict[model_name] = noise_sensitivity_tester
    
    def start_test(self):
        all_test_ans_dict = dict()
        for model_name in self.noise_sensitivity_tester_dict:
            tester = self.noise_sensitivity_tester_dict[model_name]

            # >>> test
            tester.base.net = tester.base.net.to(self.gpu_dev)
            tester.base.gpu_num = self.gpu_num
            tester.base._set_device()

            test_ans = tester.test()

            tester.base.net = tester.base.net.to(self.cpu_dev)
            tester.base.gpu_num = -1
            tester.base._set_device()
            # <<< test
            all_test_ans_dict[model_name] = test_ans
        self.all_test_ans_dict = all_test_ans_dict
    
    def summary(self):
        assert self.all_test_ans_dict != None

        # Print Title
        if self.noise_var != None:
            title = "="*10 + f" Noise Var: {self.noise_var} " + "="*10
        else:
            title = "="*10 + f" SNR: {self.snr} dB " + "="*10

        # Process Data
        ## data dim = (model_name, dataset_name)
        data = []
        model_dim = []
        for model_name in self.all_test_ans_dict:
            test_ans = self.all_test_ans_dict[model_name]
            inner_data = []
            dataset_dim = []
            for dataset_name in test_ans:
                ans = test_ans[dataset_name]
                metrics_ans = ans[0]
                inner_data.append(metrics_ans)
                dataset_dim.append(dataset_name)
            model_dim.append(model_name)
            data.append(inner_data)
        
        # Print
        h_len = len(model_dim)
        w_len = len(dataset_dim)
        print(title)
        for w in range(w_len):
            print(f"[Dataset: {dataset_dim[w]}]")
            for h in range(h_len):
                ans = data[h][w]
                print(f"\t- {model_dim[h]}: {ans}")
        