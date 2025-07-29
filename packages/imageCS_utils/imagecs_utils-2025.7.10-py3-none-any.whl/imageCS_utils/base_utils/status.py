"""
Monitor the training process and automatically occupy the designated GPU memory
At the same time, it contains a queue planning class, which is used to plan the running sequence of multiple pytorch programs.
"""
# pylint: disable=broad-exception-caught
import pickle
import os
import time
import datetime
import threading

from .gpu_holder import GPUHolder
from .shared_utils import get_gpu_memory, init_folder_path, get_optimizer_lr, argv2str

####################### Training State #######################
_DEFAULT_TRAIN_STATE_DIR_ROOT = "temp_monitor_file"

def get_train_state_logfile_name(file_dir_root, default_prefix="logfile"):
    """Automatically generate log file name"""
    while True:
        timestr = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        file_name = f"{default_prefix}_{timestr}"
        if os.path.exists(f"{file_dir_root}/{file_name}") is False:
            return file_name

class TrainStateFileWriter:
    """write training state to log file"""
    def __init__(self, tempfile_dir_root=_DEFAULT_TRAIN_STATE_DIR_ROOT) -> None:
        init_folder_path(tempfile_dir_root)
        self.tempfile_dir_root = tempfile_dir_root
        self.filename = get_train_state_logfile_name(tempfile_dir_root)
        filepath = f"{self.tempfile_dir_root}/{self.filename}"
        self.fp = open(filepath, "wb")
    
    def update_data(self, **data):
        """update data"""
        data = dict(
            timestamp = time.time(),
            **data
        )
        self.fp.seek(0)
        self.fp.truncate()
        pickle.dump(data, self.fp)
        self.fp.flush()

class TrainStateFileReader:
    """read training state from log file"""
    def __init__(self, tempfile_dir_root=_DEFAULT_TRAIN_STATE_DIR_ROOT, accept_time_threshold=20, del_time_threshold=3600) -> None:
        init_folder_path(tempfile_dir_root)
        self.tempfile_dir_root = tempfile_dir_root
        self.accept_time_threshold = accept_time_threshold
        self.del_time_threshold = del_time_threshold
    
    def get_all_dictdata(self):
        """read training state from log file"""
        filename_list = os.listdir(self.tempfile_dir_root)
        dictdata_dict = {}

        for filename in filename_list:
            filepath = f"{self.tempfile_dir_root}/{filename}"
            try:
                with open(filepath, mode="rb") as fp:
                    dictdata = pickle.load(fp)

                    saved_timestamp = dictdata["timestamp"]
                    save_path = dictdata["save_path"]
                    delta_time = time.time() - saved_timestamp

                    if delta_time < self.accept_time_threshold:
                        dictdata_dict[save_path] = dictdata
                    elif delta_time > self.del_time_threshold:
                        os.remove(filepath)
            except Exception:
                pass
        
        dictdata_list = [dictdata_dict[key] for key in sorted(dictdata_dict.keys())]
        return dictdata_list

class TrainStateWriter:
    """generate training state and write to log file"""
    def __init__(self, monitored_base, tempfile_dir_root=_DEFAULT_TRAIN_STATE_DIR_ROOT, refresh_time=1) -> None:
        self.monitored_base = monitored_base

        self.tempfile_dir_root = tempfile_dir_root
        self.tempfile_writer = TrainStateFileWriter(tempfile_dir_root=tempfile_dir_root)
        self.refresh_time = refresh_time

        self.thread_flag = True
    
    def _get_trainer_data(self):
        data = dict()
        # Get Save Path
        data["save_path"] = self.monitored_base.logger_path
        # Get GPU Num
        data["gpu_num"] = self.monitored_base.gpu_num
        # Get Learning Rate
        data["lr"] = get_optimizer_lr(self.monitored_base.opt)
        # Get Total Epoch
        data["total_epoch"] = self.monitored_base.cfg["train_config"]["epochs"]

        # Get Training Detial
        trainer_monitor_data_dict = self.monitored_base.trainer.monitor_data_dict
        if trainer_monitor_data_dict is None:
            data["has_info"] = False
        else:
            data.update(trainer_monitor_data_dict)
            data["has_info"] = True

        return data
    
    def _auto_write(self):
        while self.thread_flag:
            data = self._get_trainer_data()
            self.tempfile_writer.update_data(**data)
            time.sleep(self.refresh_time)
    
    def start(self):
        """start a thread to auto write training data to log file"""
        self.thread_flag = True
        thread = threading.Thread(
            target=self._auto_write,
            daemon=True
        )
        thread.start()
    
    def stop(self):
        """stop auto writing thread"""
        self.thread_flag = False

class TrainStateReader:
    """read and generate info from log file"""
    def __init__(self, tempfile_dir_root=_DEFAULT_TRAIN_STATE_DIR_ROOT, accept_time_threshold=20, del_time_threshold=3600, refresh_time=1, empty_time=600) -> None:
        self.tempfile_dir_root = tempfile_dir_root
        self.tempfile_reader = TrainStateFileReader(
            tempfile_dir_root = tempfile_dir_root,
            accept_time_threshold = accept_time_threshold,
            del_time_threshold = del_time_threshold
        )
        self.refresh_time = refresh_time
        self.empty_time = empty_time
        self.predict_dict = dict()
    
    def _clear_screen(self):
        os.system("clear||cls")
    
    def _empty_thread(self):
        while True:
            time.sleep(self.empty_time)
            self.predict_dict = dict()
    
    def start_empty_thread(self):
        """auto empty self.predict_dict"""
        thread = threading.Thread(
            target=self._empty_thread,
            daemon=True
        )
        thread.start()

    
    def _get_iter_num(self, start_epoch, end_epoch, start_process, end_process, total_process):
        delta_epoch = end_epoch - start_epoch
        delta_process = end_process - start_process

        iter_num = delta_epoch * total_process + delta_process
        return iter_num
    
    def _predict_finished_time(self, save_path, epoch, total_epoch, now_process, total_process, timestamp):
        if save_path in self.predict_dict:
            d = self.predict_dict[save_path]
            start_epoch = d["start_epoch"]
            start_process = d["start_process"]
            start_timestamp = d["start_timestamp"]

            if epoch == start_epoch and now_process == start_process:
                pre_finished_time_str = "Unknown"
            else:
                s2n_delta_iter = self._get_iter_num(
                    start_epoch=start_epoch,
                    end_epoch=epoch,
                    start_process=start_process,
                    end_process=now_process,
                    total_process=total_process
                )
                n2e_delta_iter = self._get_iter_num(
                    start_epoch=epoch,
                    end_epoch=total_epoch,
                    start_process=now_process,
                    end_process=total_process,
                    total_process=total_process
                )
                s2n_delta_time = timestamp - start_timestamp

                n2s_delta_time = s2n_delta_time * n2e_delta_iter / s2n_delta_iter
                pre_finished_time = timestamp + n2s_delta_time
                pre_finished_time = time.localtime(pre_finished_time)
                pre_finished_time_str = time.strftime("%Y-%m-%d %H:%M:%S", pre_finished_time)
        else:
            self.predict_dict[save_path] = dict(
                start_epoch = epoch,
                start_process = now_process,
                start_timestamp = timestamp
            )
            pre_finished_time_str = "Unknown"
        
        return pre_finished_time_str

    
    def _show_info(self, data_dict):
        gpu_num = data_dict["gpu_num"]
        save_path = data_dict["save_path"]

        print(f"[GPU: {gpu_num}] {save_path}")

        if data_dict["has_info"]:
            epoch = data_dict["epoch"]
            total_epoch = data_dict["total_epoch"]
            now_process = data_dict["now_process"]
            total_process = data_dict["total_process"]
            lr = data_dict["lr"]
            loss = data_dict["loss"]
            metrics_dict = data_dict["metrics"]
            timestamp = data_dict["timestamp"]

            pre_finished_time = self._predict_finished_time(
                save_path=save_path,
                epoch=epoch,
                total_epoch=total_epoch,
                now_process=now_process,
                total_process=total_process,
                timestamp=timestamp
            )

            print(f"\t- Epoch: {epoch} / {total_epoch} | ({now_process}/{total_process})")
            print(f"\t- Estimated completion time: {pre_finished_time}")
            print(f"\t- lr: {lr} | loss: {loss:.8f}")
            print("\t- ", end="")
            for metric_name in metrics_dict:
                print(f"{metric_name}: {metrics_dict[metric_name]:.6f}", end=" | ")
            print("\n")
        else:
            print("\t- No Info")
    
    def show_all_info(self):
        """print all training state"""
        dictdata_list = self.tempfile_reader.get_all_dictdata()
        if len(dictdata_list) == 0:
            print("No working process...")
        else:
            for dictdata in dictdata_list:
                self._show_info(dictdata)
    
    def start(self):
        """start a thread to auto read, generate and show log info"""
        self.start_empty_thread()
        while True:
            self._clear_screen()
            self.show_all_info()
            time.sleep(self.refresh_time)

####################### Queue State #######################
_DEFAULT_QUEUE_STATE_DIR_ROOT = "temp_queue_file"
_QUEUE_STATE_READER_RETRY_CHANCE_ = 20

def get_queue_state_logfile_name(file_dir_root, default_prefix="queuefile"):
    """Automatically generate log file name"""
    while True:
        timestr = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        file_name = f"{default_prefix}_{timestr}"
        if os.path.exists(f"{file_dir_root}/{file_name}") is False:
            return file_name

class QueueStateFileWriter:
    """write queue state to queue state file"""
    def __init__(self, dir_root=_DEFAULT_QUEUE_STATE_DIR_ROOT):
        init_folder_path(dir_root)
        self.dir_root = dir_root
        self.filename = get_queue_state_logfile_name(dir_root)
        filepath = f"{self.dir_root}/{self.filename}"
        self.fp = open(filepath, "wb")

    def update_data(self, start_time, name, gpu, state):
        """update queue data"""
        assert state in ["waiting", "running", "stopped"]
        data = dict(
            start_time = start_time,
            name = name,
            gpu = gpu,
            id = self.filename,
            state = state,
            reflesh_time = time.time(),
        )
        self.fp.seek(0)
        self.fp.truncate()
        pickle.dump(data, self.fp)
        self.fp.flush()

class QueueStateFileReader:
    """read queue state from queue state file"""
    def __init__(self, dir_root=_DEFAULT_QUEUE_STATE_DIR_ROOT, accept_time_threshold=20, del_time_threshold=3600):
        init_folder_path(dir_root)
        self.dir_root = dir_root
        self.accept_time_threshold = accept_time_threshold
        self.del_time_threshold = del_time_threshold
    
    def get_all_data(self):
        """generate queue data from queue state file"""
        filename_list = os.listdir(self.dir_root)
        gpu_dict = {}

        for filename in filename_list:
            filepath = f"{self.dir_root}/{filename}"
            retry_chance = _QUEUE_STATE_READER_RETRY_CHANCE_
            while retry_chance >= 0:
                try:
                    with open(filepath, mode="rb") as fp:
                        dictdata = pickle.load(fp)

                        delta_time = time.time() - dictdata["reflesh_time"]

                        if delta_time < self.accept_time_threshold:
                            gpu = dictdata["gpu"]
                            if isinstance(gpu, int) and gpu >= 0:
                                if not gpu in gpu_dict:
                                    gpu_dict[gpu] = []
                                gpu_dict[gpu].append(dictdata)
                            elif type(gpu) in (list, tuple):
                                for gpu_ in gpu:
                                    if not gpu_ in gpu_dict:
                                        gpu_dict[gpu_] = []
                                    gpu_dict[gpu_].append(dictdata)
                        elif delta_time > self.del_time_threshold:
                            os.remove(filepath)
                    retry_chance = -1
                except Exception:
                    time.sleep(0.1)
                    retry_chance -= 1
        
        data_dict = {}
        for key in sorted(gpu_dict.keys()):
            data_dict[key] = sorted(gpu_dict[key], key=lambda d: d['start_time'])
        return data_dict

class QueueStateManager:
    """
    Execute queued tasks, and set its status to "running"
    when there are no other tasks in front of the queue.
    The user can perform the tasks that need to be performed
    after this state. After the task execution is completed,
    call the "stop()" function to set its status to "stopped"
    to facilitate the execution of other tasks. During these
    processes, this module will automatically save its own state
    to the queue state file for easy viewing by other QueueStateManagers.
    """
    def __init__(self, name, gpu, dir_root=_DEFAULT_QUEUE_STATE_DIR_ROOT, accept_time_threshold=20, del_time_threshold=3600, reflesh_time=1):
        assert type(gpu) in (int, list, tuple)
        self.queue_writer = QueueStateFileWriter(dir_root=dir_root)
        self.queue_reader = QueueStateFileReader(
            dir_root=dir_root,
            accept_time_threshold=accept_time_threshold,
            del_time_threshold=del_time_threshold
        )

        self.start_time = time.time()
        self.name = name
        self.gpu = gpu
        self.state = "waiting"

        self.id = self.queue_writer.filename
        self.reflesh_time = reflesh_time
        self.running_flag = False
    
    def _update_data(self):
        self.queue_writer.update_data(
            start_time=self.start_time,
            name = self.name,
            gpu = self.gpu,
            state = self.state
        )

    
    def _reflesh(self):
        while self.running_flag:
            self._update_data()
            time.sleep(self.reflesh_time)
    
    def _start_reflesh(self):
        thread = threading.Thread(
            target=self._reflesh,
            daemon=True
        )
        thread.start()
    
    def _continue_running(self):
        data_dict = self.queue_reader.get_all_data()
        if isinstance(self.gpu, int):
            gpu_list = [self.gpu]
        else:
            gpu_list = self.gpu
        
        counter = 0
        for gpu in gpu_list:
            if gpu in data_dict:
                data_list = data_dict[gpu]
                if len(data_list) == 0:
                    counter += 1
                else:
                    first_data = data_list[0]
                    id_ = first_data["id"]
                    state = first_data["state"]
                    if id_ == self.id:
                        counter += 1
                    elif state in ("stopped"):
                        if data_list[1]["id"] == self.id:
                            counter += 1
            else:
                counter += 1
        
        l = len(gpu_list)
        assert counter <= l
        if counter == l:
            return True
        else:
            return False
    
    def start(self):
        """
        Start queuing until there are no more tasks in front of the queue.
        While queuing, its status is "waiting". After starting the task, its status is "running".
        """
        self.running_flag = True
        print(f"[{self.id}] waiting...")
        self._start_reflesh()
        while True:
            if self._continue_running() is True:
                self.state = "running"
                break
            else:
                time.sleep(self.reflesh_time)
        print(f"[{self.id}] started!")

    
    def stop(self):
        """After running all tasks, execute this function to stop queuing, and then set its status to "stopped"."""
        self.running_flag = False
        self.state = "stopped"
        self._update_data()
        print(f"[{self.id}] stopped.")
    
    def __del__(self):
        self.stop()

class QueueStateManagerArgv(QueueStateManager):
    """set command argv as name"""
    def __init__(self, argv_list, gpu, *args, **kwargs):
        argv_str = argv2str(argv_list)
        super().__init__(argv_str, gpu, *args, **kwargs)
    
class QueueStateReader:
    """read all queue state file and print thier info"""
    def __init__(self, dir_root=_DEFAULT_QUEUE_STATE_DIR_ROOT, accept_time_threshold=20, del_time_threshold=3600, reflesh_time=1):
        self.queue_reader = QueueStateFileReader(
            dir_root=dir_root,
            accept_time_threshold=accept_time_threshold,
            del_time_threshold=del_time_threshold
        )

        self.reflesh_time = reflesh_time
    
    def print_info(self, data_dict, gpu_memory_state):
        """print all queue info"""
        if len(data_dict) == 0:
            print("No working queue...")
        else:
            for gpu in data_dict:
                (used_mem, total_mem) = gpu_memory_state
                print(f"[GPU: {gpu}] ({used_mem[gpu]} MB / {total_mem[gpu]} MB)")
                data_list = data_dict[gpu]
                
                for data in data_list:
                    start_time = data["start_time"]
                    start_time = time.localtime(start_time)
                    start_time = time.strftime("%Y-%m-%d %H:%M:%S", start_time)

                    name = data["name"]
                    state = data["state"]

                    print(f" - {start_time} [{state}] ({name})")
    
    def get_all_data(self):
        """get all queue data"""
        return self.queue_reader.get_all_data()
    
    def start(self):
        """generate queue state file and print all info"""
        while True:
            data_dict = self.get_all_data()
            gpu_mem_state = get_gpu_memory()
            os.system("clear||cls")
            self.print_info(data_dict, gpu_mem_state)
            time.sleep(self.reflesh_time)

####################### Monitor #######################

class Monitor:
    """
    a Monitor to show all training state and queue state info,
    and auto hold specifity gpu memory.
    """
    def __init__(self, train_state_reader_class=TrainStateReader, queue_state_reader_class=QueueStateReader, refresh_time=1,
                 hold_gpu_list=None, queue_state_manager_class=QueueStateManager,
                 train_state_dir_root=_DEFAULT_TRAIN_STATE_DIR_ROOT, queue_state_dir_root=_DEFAULT_QUEUE_STATE_DIR_ROOT) -> None:
        #### init ####
        hold_gpu_list = [] if hold_gpu_list is None else hold_gpu_list
        #### printer ####
        self.train_state_reader = train_state_reader_class(tempfile_dir_root=train_state_dir_root)
        self.queue_state_reader = queue_state_reader_class(dir_root=queue_state_dir_root)
        self.refresh_time = refresh_time

        #### holder ####
        self.hold_gpu_list = hold_gpu_list
        self.queue_state_manager_class = queue_state_manager_class
        self.queue_state_dir_root = queue_state_dir_root
        self.queue_state_manager_dict = {}
    
    def _clear_screen(self):
        os.system("clear||cls")
    
    def _hold_gpu(self, gpu_num, queue_state_data_dict):
        if gpu_num in queue_state_data_dict:
            # Something is running in GPU
            if gpu_num in self.queue_state_manager_dict:
                # Holder is running
                if len(queue_state_data_dict[gpu_num]) >= 2:
                    # Not only Holder is running
                    self._holder_stop(gpu_num)
        else:
            # Nothing is running in GPU
            self._holder_start(gpu_num)
    
    def _hold_all_gpu(self, queue_state_data_dict):
        for gpu_num in self.hold_gpu_list:
            self._hold_gpu(gpu_num, queue_state_data_dict)
    
    def _holder_start(self, gpu_num):
        queue_state_manager = self.queue_state_manager_class(
            name = "holder",
            gpu = gpu_num,
            dir_root = self.queue_state_dir_root
        )
        gpu_holder = GPUHolder(
            sleep_time = 10,
            gpu_num = gpu_num,
            force_mode = False,
            using_process=True
        )

        self.queue_state_manager_dict[gpu_num] = (queue_state_manager, gpu_holder)
        queue_state_manager.start()
        gpu_holder.start()

    def _holder_stop(self, gpu_num):
        (queue_state_manager, gpu_holder) = self.queue_state_manager_dict.pop(gpu_num)
        gpu_holder.stop()
        queue_state_manager.stop()
    
    def start(self):
        """start all task"""
        self.train_state_reader.start_empty_thread()
        while True:
            queue_state_data_dict = self.queue_state_reader.get_all_data()
            self._hold_all_gpu(queue_state_data_dict)
            gpu_mem_state = get_gpu_memory()
            self._clear_screen()
            self.train_state_reader.show_all_info()
            print("--------------------------------------------------------------------\n")
            self.queue_state_reader.print_info(queue_state_data_dict, gpu_mem_state)
            time.sleep(self.refresh_time)
