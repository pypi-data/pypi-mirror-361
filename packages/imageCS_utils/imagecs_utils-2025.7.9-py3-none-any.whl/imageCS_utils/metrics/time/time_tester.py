import time
import torch
import os

class Time_Tester:
    def __init__(self, model):
        self.model = model
        self.model.eval()
        self.time_history = []
        self.batchsize_history = []
    
    @torch.no_grad()
    def feed(self, batch_size, *args, **kwargs):
        start_time = time.time()
        _ = self.model(*args, **kwargs)
        end_time = time.time()

        delta_time = end_time - start_time
        self.time_history.append(delta_time)
        self.batchsize_history.append(batch_size)
    
    def get_time(self, counted_epoch=None, is_avg=True):
        if counted_epoch == None:
            start_ptr = 0
        else:
            start_ptr = -counted_epoch
        
        total_time = 0
        total_batch_num = 0
        
        for (time, batch_size) in zip(self.time_history[start_ptr:], self.batchsize_history[start_ptr:]):
            total_time += time
            total_batch_num += batch_size
        
        if is_avg:
            avg_time = total_time / total_batch_num
            return avg_time
        else:
            return total_time

class Timer_Tester_Proc:
    def __init__(self, gpu_num = -1, total_epoch = 300, counted_epoch = 100, batch_size = 16, channels = 1, img_size = 256):
        self.gpu_num = gpu_num
        self.total_epoch = total_epoch
        self.counted_epoch = counted_epoch
        self.batch_size = batch_size
        self.channels = channels
        self.img_size = img_size
        if gpu_num >= 0:
            self.dev = torch.device("cuda:0")
            os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
            os.environ["CUDA_VISIBLE_DEVICES"] = str(self.gpu_num)
        else:
            self.dev = torch.device("cpu")
        self.cpu_dev = torch.device("cpu")

        self.timer_list = []

    def add_model(self, **kwargs):
        for model_name in kwargs:
            model = kwargs[model_name]
            model_timer = Time_Tester(model=model)
            self.timer_list.append((model_name, model_timer))

    def test_time(self):
        for (name, timer) in self.timer_list:
            timer.model = timer.model.to(self.dev)
            for i in range(1, self.total_epoch+1):
                print(f"({name}) {i} / {self.total_epoch}", end="\r")
                x = torch.randn((self.batch_size, self.channels, self.img_size, self.img_size), device=self.dev)
                timer.feed(self.batch_size, x)
            print()
            timer.model = timer.model.to(self.cpu_dev)

    def show_time(self, times_util="s"):
        assert times_util in ("s", "ms", "us")
        print("times:")
        for (name, timer) in self.timer_list:
            used_time = timer.get_time(counted_epoch=self.counted_epoch)
            if times_util == "s":
                print(f"{name}: {used_time}s")
            elif times_util == "ms":
                print(f"{name}: {used_time*1e3}ms")
            elif times_util == "us":
                print(f"{name}: {used_time*1e6}us")
            else:
                raise Exception("Time util is not in ('s', 'ms', 'us')")
    
    def run(self, time_util="s"):
        self.test_time()
        self.show_time(times_util=time_util)