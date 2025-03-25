import pynvml
import json
import os
import time
import socket
import datetime
import shutil
import psutil

DATA_DIR = "data"
SERVER_NAME = socket.gethostname()  # Get the server's hostname
SAVE_PATH = os.path.join(DATA_DIR, SERVER_NAME)
os.makedirs(SAVE_PATH, exist_ok=True)  # Ensure directory exists

def get_free_disk_space_dict():
    possible_disk_paths = ["/home", "/extra_home", "/extra_home2", "/extra_home3", "/media/external"]
    free_disk_space_dict = {}

    for disk_path in possible_disk_paths:
        if os.path.exists(disk_path):
            total, used, free = shutil.disk_usage(disk_path)
            free_gb = free / (2**30)
            free_disk_space_dict[disk_path] = free_gb
    
    return free_disk_space_dict

def save_gpu_stats(log_utils=False, log_days=3):
    util_log_path = os.path.join(SAVE_PATH, "utils_log.json")
    gpu_stats_path = os.path.join(SAVE_PATH, "gpu_stats.json")


    if os.path.exists(util_log_path):
        with open(util_log_path, "r") as f:
            util_avg_list = json.load(f)['util_avg_list']
    else:
        util_avg_list = None

    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()
    gpu_data = []

    for i in range(gpu_count):
        unix_timestamp = datetime.datetime.now().timestamp()
        free_disk_space_dict = get_free_disk_space_dict()
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

            users = set()
            processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
            for process in processes:
                try:
                    user = psutil.Process(process.pid).username()
                    users.add(user)
                except psutil.NoSuchProcess:
                    pass  # Process may have terminated


            gpu_data.append({
                "id": i,
                "name": name,
                "memory_used": mem_info.used / 1024**3,  # GB
                "memory_total": mem_info.total / 1024**3,
                "utilization": util.gpu,
                "three_day_avg_util": util_avg_list[i] if util_avg_list is not None else -1,
                "temperature": temperature,
                "free_disk_space_dict": free_disk_space_dict,
                "unix_timestamp": unix_timestamp,
                "error": False,
                "error_message": "",
                "users": list(users)
            })

        
        except Exception as e:
            gpu_data.append({
                "id": i,
                "name": str(e),
                "memory_used": 0,  # GB
                "memory_total": 0.1,
                "utilization": 0,
                "three_day_avg_util": util_avg_list[i] if util_avg_list is not None else -1,
                "temperature": -1,
                "free_disk_space_dict": free_disk_space_dict,
                "unix_timestamp": unix_timestamp,
                "error": True,
                "error_message": str(e),
                "users": []
            })
    
    #print(gpu_data)

    pynvml.nvmlShutdown()

    # Save to JSON file under this server's folder
    with open(gpu_stats_path, "w") as f:
        json.dump(gpu_data, f, indent=4)
    
    if log_utils:
        new_util_log_dict = []
        util_avg_list = [0 for i in range(gpu_count)]
        util_avg_count_list = [1e-9 for i in range(gpu_count)]


        if os.path.exists(util_log_path):
            with open(util_log_path, "r") as f:
                util_log_json = json.load(f)
                util_log_dict = util_log_json['util_log_dict']
            
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(days=log_days)

            for util_log_entry in util_log_dict:
                timestamp = datetime.datetime.fromtimestamp(util_log_entry[0]["unix_timestamp"])
                if start_time <= timestamp <= end_time:
                    new_util_log_dict.append(util_log_entry)

                    for per_gpu_data in util_log_entry:
                        util_avg_list[int(per_gpu_data['id'])] += per_gpu_data['utilization']
                        util_avg_count_list[int(per_gpu_data['id'])] += 1

        new_util_log_dict.append(gpu_data)  
        for per_gpu_data in gpu_data:
            util_avg_list[int(per_gpu_data['id'])] += per_gpu_data['utilization']
            util_avg_count_list[int(per_gpu_data['id'])] += 1

        new_util_avg_list = [util_avg_list[i] / util_avg_count_list[i] for i in range(gpu_count)]
        
        print(util_avg_count_list)      

        with open(util_log_path, "w") as f:
            json.dump({"util_log_dict": new_util_log_dict, "util_avg_list": new_util_avg_list}, f, indent=4)



if __name__ == "__main__":
    save_gpu_stats_every_n_second = 5
    log_utils_every_n_second = 60 * 30

    assert (log_utils_every_n_second // save_gpu_stats_every_n_second) > 1
    counter = 0

    time.sleep(120) # delay until system is fully rebooted

    while True:
        if counter != log_utils_every_n_second // save_gpu_stats_every_n_second:
            save_gpu_stats(log_utils=False)
        else:
            save_gpu_stats(log_utils=True)
            counter = 0

        time.sleep(save_gpu_stats_every_n_second)  # Update every 5 seconds
        counter += 1
