"""Trainer: train and auto save training processing"""
import torch
from tqdm import tqdm
from .shared_utils import TimeStatistic, DictUpdate, tensor_detach_and_cpu

class Trainer:
    """deprecated, please use MetricsTrainer or UniversalMetricsTrainer instead."""
    def __init__(self, *args, **kwargs):
        """deprecated function"""
        raise RuntimeError("Trainer has been deprecated, please use MetricsTrainer or UniversalMetricsTrainer instead.")

class MetricsTrainer:
    """
    train and auto save training processing
    you should first set the metrics function
    """
    def __init__(self, net:torch.nn.Module, loss:torch.nn.Module, opt, dev, logger, lr_scheduler_list=None, other_data_dict=None, delay_backward_step=None):
        other_data_dict = {} if other_data_dict is None else other_data_dict

        self.net = net
        self.loss = loss
        self.opt = opt
        self.dev = dev
        self.logger = logger
        self.lr_scheduler_list = lr_scheduler_list
        self.other_data_dict = other_data_dict

        self.monitor_data_dict = None
        self.time_statistic = TimeStatistic()
        self.time_statistic_flag = False

        # Delay n Step to backward loss
        self.delay_backward_step = delay_backward_step
        self.delay_backward_counter = delay_backward_step
        self.delay_loss = 0.0
    
    def _enable_time_statistic(self):
        self.time_statistic_flag = True

    def _disable_time_statistic(self):
        self.time_statistic_flag = False

    def _data_prepare(self, mini_batch_data):
        (x, y) = mini_batch_data
        x = x.to(self.dev)
        y = y.to(self.dev)
        data = (x, y)
        return data
    
    def _net_forward(self, data_prepare_output):
        (x, _) = data_prepare_output
        if self.time_statistic_flag:
            self.time_statistic.start()

        net_output = self.net(x)

        if self.time_statistic_flag:
            self.time_statistic.stop()

        return net_output
    
    def _loss_forward(self, data_prepare_output, net_forward_output):
        (_, y) = data_prepare_output
        y_pred = net_forward_output
        loss = self.loss(y_pred, y)
        return loss
    
    def _loss_backward(self, loss):
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

    def _delay_loss_backward(self, loss):
        self.delay_backward_counter -= 1
        self.delay_loss += loss
        if self.delay_backward_counter <= 0:
            self._loss_backward(self.delay_loss)
            self.delay_backward_counter = self.delay_backward_step
            self.delay_loss = 0.0
    
    def _update_lr(self):
        for lr_scheduler in self.lr_scheduler_list:
            lr_scheduler.step()
    
    def _get_mini_batch_size(self, data_prepare_output):
        (x, _) = data_prepare_output
        return len(x)
    
    def _get_dataset_num(self, dataloader):
        l = len(dataloader.dataset)
        return l

    def _metrics_forward(self, metrics_func_dict, data_prepare_output, net_forward_output):
        metrics_dict = {}
        metrics_kwargs = self._set_metrics_kwargs(data_prepare_output, net_forward_output)
        for metrics_name in metrics_func_dict:
            metrics_func = metrics_func_dict[metrics_name]
            metrics_data = metrics_func(**(metrics_kwargs[metrics_name]))
            metrics_dict[metrics_name] = metrics_data
        return metrics_dict

    def _set_metrics_kwargs(self, data_prepare_output, net_forward_output):
        """
        # Example

        ## In some where define acc function
        def mse_func(y, y_pred):
            return (y - y_pred).pow(2).mean()
        
        def psnr_func(x1, x2):
            ...
            return psnr

        ## In cfg
        "train_config": {
            "metrics_func_dict": {
                "mse": mse_func,
                "psnr": psnr_func
            },
            ...
        }

        ## In this function
        (_, y) = data_prepare_output
        y_pred = net_forward_output
        kwargs = {
            "mse": {
                "y": y,
                "y_pred": y_pred
            },
            "psnr": {
                "x1": y,
                "x2": y_pred
            }
        }
        return kwargs

        ## after that, the trainer will run such:
        mse_ans = mse_func(y=y, y_pred=y_pred)
        psnr_ans = psnr_func(x1=y, x2=y_pred)
        """
        raise NotImplementedError
    
    def _update_pbar(self, pbar:tqdm, epoch, batch_size, loss, metrics_dict):
        if isinstance(loss, torch.Tensor):
            postfix = {'loss': loss.item()}
        else:
            postfix = {'loss': loss}

        for metrics_name, metrics in metrics_dict.items():
            if isinstance(metrics, torch.Tensor):
                postfix.update({metrics_name: metrics.item()})
            else:
                postfix.update({metrics_name: metrics})
        if epoch is not None:
            postfix["epoch"] = epoch

        pbar.set_postfix(postfix)
        pbar.update(batch_size)
    
    def _update_monitor(self, total_process, now_process, epoch, batch_size, loss, metrics_dict, backward):
        now_process += batch_size
        if backward and epoch is not None:
            monitor_metric_dict = dict()
            for metrics_name, metrics in metrics_dict.items():
                monitor_metric_dict[metrics_name] = metrics.item()
            self.monitor_data_dict = dict(
                epoch = epoch,
                now_process = now_process,
                total_process = total_process,
                loss = loss.item(),
                metrics = monitor_metric_dict
            )

        if self.time_statistic_flag:
            self.time_statistic.step(step_num=batch_size)

        return now_process
    
    def _forward(self, mini_batch_data, metrics_func_dict):
            data_prepare_output = self._data_prepare(mini_batch_data)
            net_forward_output = self._net_forward(data_prepare_output)
            loss = self._loss_forward(data_prepare_output, net_forward_output)
            metrics_dict = self._metrics_forward(metrics_func_dict, data_prepare_output, net_forward_output)

            return (data_prepare_output, net_forward_output, loss, metrics_dict)
    
    def _backward(self, loss):
        if self.delay_backward_step is None:
            self._loss_backward(loss)
        else:
            self._delay_loss_backward(loss)
        
    def _iterate_dataset(self, dataloader, metrics_func_dict, backward, epoch=None, return_inner_data=False):
        pbar = tqdm(range(self._get_dataset_num(dataloader)), leave=True)

        # Inner data
        if return_inner_data:
            loss_list = []
            metrics_dict_list = []
            data_prepare_output_list = []
            net_forward_output_list = []

        # Init Loss and Metrics
        total_loss = 0.0
        total_metrics_dict = {}
        now_process = 0
        total_process = self._get_dataset_num(dataloader)

        for metrics_name in metrics_func_dict:
            total_metrics_dict[metrics_name] = 0.0

        # Iteration
        for mini_batch_data in dataloader:
            ## Data -> Net -> Outp
            (data_prepare_output, net_forward_output, loss, metrics_dict) = self._forward(mini_batch_data, metrics_func_dict)
            batch_size = self._get_mini_batch_size(data_prepare_output)

            ## Loss backward
            if backward:
                self._backward(loss)
            
            ## Update pbar
            self._update_pbar(pbar, epoch, batch_size, loss, metrics_dict)

            ## Update total loss & total metrics
            total_loss += loss.item()
            for metrics_name, metrics in metrics_dict.items():
                total_metrics_dict[metrics_name] += metrics.item()

            ## Update monitor
            now_process = self._update_monitor(total_process, now_process, epoch, batch_size, loss, metrics_dict, backward)
            
            ## Update inner data
            if return_inner_data:
                loss_list.append(tensor_detach_and_cpu(loss))
                metrics_dict_list.append(tensor_detach_and_cpu(metrics_dict))
                data_prepare_output_list.append(tensor_detach_and_cpu(data_prepare_output))
                net_forward_output_list.append(tensor_detach_and_cpu(net_forward_output))
        
        # End and calculate loss & metrics
        avg_loss = total_loss / len(dataloader)
        avg_metrics_dict = {}
        for metrics_name in metrics_dict:
            avg_metrics_dict[metrics_name] = total_metrics_dict[metrics_name] / len(dataloader)

        # Set Ended pbar
        self._update_pbar(pbar, epoch, 0, avg_loss, avg_metrics_dict)
        pbar.close()

        # Return
        if return_inner_data:
            return (avg_loss, avg_metrics_dict, loss_list, metrics_dict_list, data_prepare_output_list, net_forward_output_list)
        return (avg_loss, avg_metrics_dict)
    
    def test(self, dataloader, metrics_func_dict):
        """default test function"""
        with torch.no_grad():
            self.net.eval()
            self._enable_time_statistic()
            self.time_statistic.clear()
            (avg_loss, avg_metrics_dict, loss_list, metrics_dict_list, data_prepare_output_list, net_forward_output_list) = self._iterate_dataset(
                dataloader,
                metrics_func_dict,
                backward=False,
                return_inner_data=True
            )
            avg_time = self.time_statistic.statistic()
            self._disable_time_statistic()

            print("======= Test Result =======")
            ans = f'avg_loss = {avg_loss}'
            for metrics_name, avg_metrics in avg_metrics_dict.items():
                ans = ans + f'\navg_{metrics_name} = {avg_metrics}'
            ans = ans + f'\navg_time = {avg_time}s'
            print(ans)
            print("===========================")

        return (avg_loss, avg_metrics_dict, avg_time, loss_list, metrics_dict_list, data_prepare_output_list, net_forward_output_list)

    def train(self, train_dataloader, eval_dataloader, metrics_func_dict, checkpoint_epoch, eval_epochs, epochs, gpu_holder=None):
        """train function"""
        assert self.logger.get_epoch() <= epochs
        assert eval_epochs <= checkpoint_epoch
        for epoch in range(self.logger.get_epoch() + 1, epochs + 1):
            self.net.train()
            (train_avg_loss, train_avg_metrics_dict) = self._iterate_dataset(train_dataloader, metrics_func_dict, backward=True, epoch=epoch)    
            if self.lr_scheduler_list is not None:
                self._update_lr()

            self.logger.log_train(epoch, loss=train_avg_loss, **train_avg_metrics_dict)
            self.logger.update_avg_loss(train_avg_loss)
            self.logger.add_epoch()

            if epoch % eval_epochs == 0:
                self.val(epoch, eval_dataloader, metrics_func_dict, gpu_holder)

            if epoch % checkpoint_epoch == 0:
                self.logger.save()
            else:
                self.logger.save_temp()

    def val(self, epoch, eval_dataloader, metrics_func_dict, gpu_holder=None):
        if gpu_holder is not None:
            gpu_holder.stop()
        with torch.no_grad():
            self.net.eval()
            (eval_avg_loss, eval_avg_metrics_dict) = self._iterate_dataset(eval_dataloader, metrics_func_dict, backward=False)    
            self.logger.log_eval(epoch, loss=eval_avg_loss, **eval_avg_metrics_dict)
        if gpu_holder is not None:
            gpu_holder.start()
            
class UniversalMetricsTrainer(MetricsTrainer):
    """
    train and auto save training processing,
    you should first set the metrics function.
    It maps the inputs of different processes to the independent variables of the process function
    through dictionary mapping, thereby realizing a universal Trainer.
    That is, you only need to modify the mapping dictionary in the
    configuration file to implement different training processes,
    without inheriting this class and rewriting the relevant functions
    of the training process.
    """
    def __init__(self, net, loss, opt, dev, logger, 
                    data_prepare_output_keys:list, net_forward_output_keys:list, to_dev_keys:list, net_kwargs_map:dict, loss_kwargs_map:dict, batch_size_sample_key:str,
                    lr_scheduler_list=None, other_data_dict=None, delay_backward_step=None):
        """
        #### data_prepare_output_keys
        data_prepare_output = dict()
        data_prepare_output[data_prepare_output_keys[i]] = mini_batch_data[i]
        return data_prepare_output

        #### net_forward_output_keys
        Operation is as same as data_prepare_output_keys.

        #### to_dev_keys
        out[to_dev_keys[i]] = out[to_dev_keys[i]].to(device)

        #### net_kwargs_map
        kwargs = dict()
        kwargs[key] = out[net_kwargs_map[key]]
        return net(**kwargs)

        #### loss_kwargs_map
        loss_kwargs_map = {"data_prepare_output": xxxxx, "net_forward_outpt": xxxxxx}
        And then the operation is as same as net_kwargs_map.

        #### batch_size_sample_key
        sample = data_prepare_output[batch_size_sample_key]
        batch_size = len(sample)
        """
        super().__init__(net, loss, opt, dev, logger, lr_scheduler_list, other_data_dict, delay_backward_step)
        other_data_dict = {} if other_data_dict is None else other_data_dict

        self.data_prepare_output_keys = data_prepare_output_keys
        self.net_forward_output_keys = net_forward_output_keys
        self.to_dev_keys = to_dev_keys
        self.net_kwargs_map = net_kwargs_map
        self.loss_kwargs_map = loss_kwargs_map
        self.batch_size_sample_key = batch_size_sample_key
    
    def _set_metrics_kwargs(self, data_prepare_output, net_forward_output):
        """
        # Example

        ## In some where define acc function
        def mse_func(y, y_pred):
            return (y - y_pred).pow(2).mean()
        
        def psnr_func(x1, x2):
            ...
            return psnr

        ## In cfg
        "train_config": {
            "metrics_func_dict": {
                "mse": mse_func,
                "psnr": psnr_func
            },
            ...
        }

        ## In this function
        (_, y) = data_prepare_output
        y_pred = net_forward_output
        kwargs = {
            "mse": {
                "y": y,
                "y_pred": y_pred
            },
            "psnr": {
                "x1": y,
                "x2": y_pred
            }
        }
        return kwargs

        ## after that, the trainer will run such:
        mse_ans = mse_func(y=y, y_pred=y_pred)
        psnr_ans = psnr_func(x1=y, x2=y_pred)
        """
        raise NotImplementedError
    
    def _data_prepare(self, mini_batch_data):
        if type(mini_batch_data) in [tuple, list]:
            data_prepare_output = dict()
            for (idx, key) in enumerate(self.data_prepare_output_keys):
                data_prepare_output[key] = mini_batch_data[idx]
            for key in self.to_dev_keys:
                data_prepare_output[key] = data_prepare_output[key].to(self.dev)
        else:
            assert len(self.data_prepare_output_keys) == 1
            data_prepare_output = dict()
            key = self.data_prepare_output_keys[0]
            data_prepare_output[key] = mini_batch_data
            for key in self.to_dev_keys:
                data_prepare_output[key] = data_prepare_output[key].to(self.dev)
        
        return data_prepare_output
    
    def _net_forward(self, data_prepare_output):
        net_kwargs = dict()
        for net_kwargs_key in self.net_kwargs_map:
            data_prepare_output_key = self.net_kwargs_map[net_kwargs_key]
            net_kwargs[net_kwargs_key] = data_prepare_output[data_prepare_output_key]
        
        if self.time_statistic_flag:
            self.time_statistic.start()

        net_output = self.net(**net_kwargs)

        if self.time_statistic_flag:
            self.time_statistic.stop()

        if type(net_output) in [tuple, list]:
            net_forward_output = dict()
            for (idx, key) in enumerate(self.net_forward_output_keys):
                net_forward_output[key] = net_output[idx]
        else:
            assert len(self.net_forward_output_keys) == 1
            net_forward_output = dict()
            key = self.net_forward_output_keys[0]
            net_forward_output[key] = net_output

        return net_forward_output
    
    def _loss_forward(self, data_prepare_output, net_forward_output):
        loss_kwargs = dict()

        if "data_prepare_output" in self.loss_kwargs_map:
            for loss_kwargs_key in self.loss_kwargs_map["data_prepare_output"]:
                data_prepaare_output_key = self.loss_kwargs_map["data_prepare_output"][loss_kwargs_key]
                loss_kwargs[loss_kwargs_key] = data_prepare_output[data_prepaare_output_key]
        if "net_forward_output" in self.loss_kwargs_map:
            for loss_kwargs_key in self.loss_kwargs_map["net_forward_output"]:
                net_forward_output_key = self.loss_kwargs_map["net_forward_output"][loss_kwargs_key]
                loss_kwargs[loss_kwargs_key] = net_forward_output[net_forward_output_key]
        
        loss = self.loss(**loss_kwargs)
        return loss
    
    def _get_mini_batch_size(self, data_prepare_output):
        sample = data_prepare_output[self.batch_size_sample_key]
        return len(sample)

class UniversalTrainer(UniversalMetricsTrainer):
    def __init__(self, net, loss, opt, dev, logger,
                    data_prepare_output_keys:list, net_forward_output_keys:list, to_dev_keys:list, net_kwargs_map:dict, loss_kwargs_map:dict, metrics_kwargs_map:dict, metrics_kwargs_config:dict, batch_size_sample_key:str,
                    lr_scheduler_list=None, other_data_dict=None, delay_backward_step=None, ignore_training_metrics:list[str]=[]):
        super().__init__(net, loss, opt, dev, logger, data_prepare_output_keys, net_forward_output_keys, to_dev_keys, net_kwargs_map, loss_kwargs_map, batch_size_sample_key, lr_scheduler_list, other_data_dict, delay_backward_step)
        self.metrics_kwargs_map = metrics_kwargs_map
        self.metrics_kwargs_config = metrics_kwargs_config
        self.ignore_training_metrics = ignore_training_metrics

        self.training_flag = False
    
    def _get_metrics_kwargs(self, metrics_name, data_prepare_output, net_forward_output):
        metrics_kwargs = {}
        metrics_kwargs_map = self.metrics_kwargs_map[metrics_name]
        metrics_kwargs_config = self.metrics_kwargs_config[metrics_name]

        # set input for metrics
        if "data_prepare_output" in metrics_kwargs_map:
            for metrics_kwargs_key in metrics_kwargs_map["data_prepare_output"]:
                data_prepare_output_key = metrics_kwargs_map["data_prepare_output"][metrics_kwargs_key]
                metrics_kwargs[metrics_kwargs_key] = data_prepare_output[data_prepare_output_key]
        if "net_forward_output" in metrics_kwargs_map:
            for metrics_kwargs_key in metrics_kwargs_map["net_forward_output"]:
                net_forward_output_key = metrics_kwargs_map["net_forward_output"][metrics_kwargs_key]
                metrics_kwargs[metrics_kwargs_key] = net_forward_output[net_forward_output_key]
        
        for key, value in metrics_kwargs_config.items():
            DictUpdate.insert(metrics_kwargs, value, key)
        
        return metrics_kwargs
    
    def _metrics_forward(self, metrics_func_dict, data_prepare_output, net_forward_output, ignore_metrics:list[str]=[]):
        metrics_dict = {}
        for metrics_name in metrics_func_dict:
            if metrics_name in ignore_metrics:
                pass
            else:
                metrics_func = metrics_func_dict[metrics_name]
                metrics_kwargs = self._get_metrics_kwargs(metrics_name, data_prepare_output, net_forward_output)
                metrics_data = metrics_func(**metrics_kwargs)
                metrics_dict[metrics_name] = metrics_data
        return metrics_dict
    
    def _forward(self, mini_batch_data, metrics_func_dict):
            data_prepare_output = self._data_prepare(mini_batch_data)
            net_forward_output = self._net_forward(data_prepare_output)
            loss = self._loss_forward(data_prepare_output, net_forward_output)

            if self.training_flag:
                metrics_dict = self._metrics_forward(metrics_func_dict, data_prepare_output, net_forward_output, ignore_metrics=self.ignore_training_metrics)
            else:
                metrics_dict = self._metrics_forward(metrics_func_dict, data_prepare_output, net_forward_output)

            return (data_prepare_output, net_forward_output, loss, metrics_dict)
    
    def train(self, train_dataloader, eval_dataloader, metrics_func_dict, checkpoint_epoch, eval_epochs, epochs, gpu_holder=None):
        with TrainingFlag(self, True):
            return super().train(train_dataloader, eval_dataloader, metrics_func_dict, checkpoint_epoch, eval_epochs, epochs, gpu_holder)
    
    def val(self, epoch, eval_dataloader, metrics_func_dict, gpu_holder=None):
        with TrainingFlag(self, False):
            return super().val(epoch, eval_dataloader, metrics_func_dict, gpu_holder)
    
    def test(self, dataloader, metrics_func_dict):
        with TrainingFlag(self, False):
            return super().test(dataloader, metrics_func_dict)

class TrainingFlag:
    def __init__(self, universal_trainer:UniversalTrainer, inner_training_flag:bool):
        self.universal_trainer = universal_trainer
        self.now_training_flag = universal_trainer.training_flag
        self.inner_training_flag = inner_training_flag
    
    def __enter__(self):
        self.universal_trainer.training_flag = self.inner_training_flag
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.universal_trainer.training_flag = self.now_training_flag
