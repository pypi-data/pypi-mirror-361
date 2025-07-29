"""Easy way to create, community and share data between Process"""
import inspect

from typing import Dict, List
from copy import copy
import time

from multiprocessing import Process, Pipe, Manager, Lock
from multiprocessing.connection import Connection as ConnectionClass
from multiprocessing.managers import ListProxy as ListProxyClass
from multiprocessing.managers import DictProxy as DictProxyClass
from multiprocessing.synchronize import Lock as LockClass

from threading import Thread

from .info import Info

def get_func_args_name(func) -> list:
    """get func args names"""
    return inspect.getfullargspec(func).args

class ProcManager:
    """
    Use to start child process, and handle the process communities and informations.
    """
    def __init__(self) -> None:
        self.__procs_dict:Dict[str, Process] = dict()
        self.__pipes_dict:Dict[str, ConnectionClass] = dict()
        self.__proc_name_list:List[str] = list()
        self.__info_lock = Lock()

        self.__shared_list = Manager().list()
        self.__shared_dict = Manager().dict()

        self.__shared_list_lock = Lock()
        self.__shared_dict_lock = Lock()

        self.__pipe_threads_running_dict:Dict[str, bool] = dict()
    
    def start_proc(self, proc_name:str, func, *func_args, **func_kwargs):
        """
        Start a process by specifying a function.
        Make sure the proc_name is unique and is not "__manager__" or "__all__".
        Make sure your function has parmas::this_proc at last to handle shared data of processing.
        """
        assert not proc_name in ["__manager__", "__all__"]
        assert not proc_name in self.__procs_dict
        assert not proc_name in self.__pipes_dict
        assert not proc_name in self.__proc_name_list

        this_func_args = get_func_args_name(func)
        assert this_func_args[-1] == "this_proc"
        assert not "proc_name" in this_func_args
        assert not "func" in this_func_args
        assert not "func_args" in this_func_args
        assert not "func_kwargs" in this_func_args

        (self_pipe, child_pipe) = Pipe()

        child_proc = ProcChild(
            proc_name = proc_name,
            pipe = child_pipe,
            shared_list = self.__shared_list,
            shared_dict = self.__shared_dict,
            shared_list_lock = self.__shared_list_lock,
            shared_dict_lock = self.__shared_dict_lock,
            func = func,
            func_args = func_args,
            func_kwargs = func_kwargs
        )

        self.__link_child_proc(
            proc_name = proc_name,
            child_proc = child_proc,
            self_pipe = self_pipe
        )

        try:
            child_proc.start()
            self.__start_recv_msg_thread(
                proc_name = proc_name,
                self_pipe = self_pipe
            )
        except RuntimeError as e:
            Info.error(str(e))
            self.__unlink_child_proc(proc_name)
        
        return child_proc
    
    def wait(self):
        while self.__proc_name_list:
            time.sleep(0.1)
    
    def get_proc(self, name):
        """get the child proc via proc name"""
        with self.__info_lock:
            assert name in self.__proc_name_list
            proc = self.__proc_name_list[name]
        return proc
    
    def get_all_proc_name(self):
        """get all running child proc name list"""
        with self.__info_lock:
            proc_name_list = list(self.__proc_name_list)
        return proc_name_list

    def __link_child_proc(self, proc_name, child_proc, self_pipe):
        with self.__info_lock:
            self.__procs_dict[proc_name] = child_proc
            self.__pipes_dict[proc_name] = self_pipe
            self.__proc_name_list.append(proc_name)

    def __unlink_child_proc(self, proc_name):
        with self.__info_lock:
            assert proc_name in self.__procs_dict
            assert proc_name in self.__pipes_dict
            assert proc_name in self.__proc_name_list

            _ = self.__procs_dict.pop(proc_name)
            _ = self.__pipes_dict.pop(proc_name)
            self.__proc_name_list.remove(proc_name)

    def get_shared_list(self):
        """get the copy of self.__shared_list"""
        return list(self.__shared_list)

    def get_shared_dict(self):
        """get the copy of self.__shared_dict"""
        return dict(self.__shared_dict)
    
    def __handle_pipe_data(self, msg:dict, proc_name:str):
        sender_name:str = msg["sender_name"]
        receiver_name:str = msg["receiver_name"]
        command:str = msg["command"]
        data = msg["data"]
        sender_proc_pipe:ConnectionClass|None = msg["pipe"]

        match receiver_name:
            case "__manager__":
                match command:
                    case "proc finished":
                        self.__pipe_threads_running_dict[proc_name] = False
                        self.__unlink_child_proc(sender_name)
                        #Info.info(f"Finished {sender_name}")
                    case "proc started":
                        #Info.info(f"Started {sender_name}")
                        pass
                    case "proc exist":
                        check_proc_name = data
                        assert sender_proc_pipe is not None
                        with self.__info_lock:
                            ans_bool = check_proc_name in self.__proc_name_list
                        sender_proc_pipe.send(ans_bool)
                    case _:
                        s = f"Unexcepted command [{command}] from {sender_name}."
                        Info.error(s)
            case "__all__":
                with self.__info_lock:
                    all_proc_name = list(self.__proc_name_list)
                for recv_name in all_proc_name:
                    if recv_name != sender_name:
                        self.__pipes_dict[recv_name].send(msg)
            case _:
                self.__pipes_dict[receiver_name].send(msg)
    
    def __thread_recv_msg(self, proc_name:str, self_pipe:ConnectionClass):
        self.__pipe_threads_running_dict[proc_name] = True
        while self.__pipe_threads_running_dict[proc_name]:
            try:
                msg = self_pipe.recv()
                self.__handle_pipe_data(
                    msg = msg,
                    proc_name = proc_name,
                )
            except EOFError:
                Info.info(f"EOF {proc_name}")
                self.__pipe_threads_running_dict[proc_name] = False
        #Info.info(f"End thread {proc_name}")
    
    def __start_recv_msg_thread(self, proc_name:str, self_pipe:ConnectionClass):
        thread = Thread(
            target=self.__thread_recv_msg,
            kwargs=dict(
                proc_name = proc_name,
                self_pipe = self_pipe
            )
        )
        thread.start()

class ProcChild(Process):
    """child process, started by ProcCore"""
    def __init__(
            self, proc_name:str, pipe:ConnectionClass,
            shared_list:ListProxyClass, shared_dict:DictProxyClass,
            shared_list_lock:LockClass, shared_dict_lock:LockClass,
            func, func_args:tuple, func_kwargs:dict):
        super().__init__(
            target=func,
            name=proc_name,
            args=func_args,
            kwargs=func_kwargs
        )
        self.__proc_name = proc_name
        self.__pipe = pipe

        self.__shared_list = shared_list
        self.__shared_dict = shared_dict

        self.__shared_list_lock = shared_list_lock
        self.__shared_dict_lock = shared_dict_lock

        self.__func = func
        self.__func_args = func_args
        self.__func_kwargs = func_kwargs

        self.__default_self_pipe, self.__default_target_pipe = Pipe()
    

    def run(self):
        """start running"""
        # tell the core, we have started
        self.send_msg(
            target_name="__manager__",
            command="proc started"
        )

        # start function
        self.__func(*(self.__func_args), **(self.__func_kwargs), this_proc=self)

        # tell the core, we have finished
        self.send_msg(
            target_name="__manager__",
            command="proc finished"
        )
    
    def send_msg(self, target_name:str, command, data=None, pipe:ConnectionClass|None=None):
        """send msg (command and data) via pipe"""
        msg = dict(
            sender_name = self.__proc_name,
            receiver_name = target_name,
            command = command,
            data = data,
            pipe = pipe
        )
        self.__pipe.send(msg)
    
    def send_msg_all(self, command, data=None, pipe:ConnectionClass|None=None):
        """send msg to all"""
        self.send_msg(
            target_name = "__all__",
            command = command,
            data = data,
            pipe = pipe
        )
    
    def send_and_recv(self, target_name:str, command, data=None, pipe_self:ConnectionClass|None=None, pipe_target:ConnectionClass|None=None):
        """send msg and auto recv. Return the recv data"""
        if pipe_self is None and pipe_target is None:
            pipe_self = self.__default_self_pipe
            pipe_target = self.__default_target_pipe
        else:
            assert pipe_self is not None
            assert pipe_target is not None

        self.send_msg(
            target_name = target_name,
            command = command,
            data = data,
            pipe = pipe_target
        )

        return pipe_self.recv()
    
    def recv_msg(self):
        """receive msg (command and data) via pipe"""
        msg:dict = self.__pipe.recv()
        sender_name:str = msg["sender_name"]
        command = msg["command"]
        data = msg["data"]
        pipe:ConnectionClass = msg["pipe"]

        return (sender_name, command, data, pipe)

    def shared_list_append(self, data):
        """append data to list"""
        with self.__shared_list_lock:
            self.__shared_list.append(data)


    def shared_list_pop(self, idx:int):
        """pop data from list"""
        with self.__shared_list_lock:
            data = self.__shared_list.pop(idx)
        return data

    def shared_dict_update(self, key, data):
        """update shared dict"""
        with self.__shared_dict_lock:
            self.__shared_dict[key] = data

    def get_from_shared_list(self, idx:int):
        """get data from shared list via index"""
        with self.__shared_list_lock:
            data = self.__shared_list[idx]
        return data
    
    def get_from_shared_dict(self, key):
        """get data from shared dict via key"""
        with self.__shared_dict_lock:
            data = self.__shared_dict[key]
        return data

    def shared_list_copy(self):
        """get the copy of self.__shared_list"""
        with self.__shared_list_lock:
            list_copy = list(self.__shared_list)
        return list_copy
    
    def shared_dict_copy(self):
        """get the copy of self.__shared_dict"""
        with self.__shared_dict_lock:
            dict_copy = dict(self.__shared_dict)
        return dict_copy

    def get_proc_name(self):
        return copy(self.__proc_name)
    
    def check_proc_exist(self, proc_name:str):
        return self.send_and_recv(
            target_name = "__manager__",
            command = "proc exist",
            data = proc_name,
        )

def __example_func(in_data:int, this_proc:ProcChild):
    """an example function in child process, you must include args named "this_proc" to process the child process"""
    print(f"Proc {this_proc.name} start running, func args is {in_data}")

    this_proc.send_msg(
        target_name = "__all__",
        command = "added in_data",
        data = in_data + 1
    )

if __name__ == "__main__":
    pc = ProcManager()
    cp = pc.start_proc(
        proc_name = "example",
        func = __example_func,
        in_data = 12
    )
    cp.join()
    pc.wait()
