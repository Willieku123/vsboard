import pynvml
import json
import os
import time
import socket
import datetime
import shutil

DATA_DIR = "data"
SERVER_NAME = socket.gethostname()  # Get the server's hostname
SAVE_PATH = os.path.join(DATA_DIR, SERVER_NAME)
os.makedirs(SAVE_PATH, exist_ok=True)  # Ensure directory exists

def get_free_disk_space_dict():
    possible_disk_paths = ["/home", "/extra_home", "/extra_home2", "/extra_home3"]
    free_disk_space_dict = {}

    for disk_path in possible_disk_paths:
        if os.path.exists(disk_path):
            total, used, free = shutil.disk_usage(disk_path)
            free_gb = free / (2**30)
            free_disk_space_dict[disk_path] = free_gb
    
    return free_disk_space_dict

def save_gpu_stats():
    pynvml.nvmlInit()
    gpu_count = pynvml.nvmlDeviceGetCount()
    gpu_data = []

    for i in range(gpu_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        name = pynvml.nvmlDeviceGetName(handle)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        free_disk_space_dict = get_free_disk_space_dict()
        unix_timestamp = datetime.datetime.now().timestamp()

        gpu_data.append({
            "id": i,
            "name": name,
            "memory_used": mem_info.used / 1024**2,  # MB
            "memory_total": mem_info.total / 1024**2,
            "utilization": util.gpu,
            "temperature": temperature,
            "free_disk_space_dict": free_disk_space_dict,
            "unix_timestamp": unix_timestamp
        })
    
    #print(gpu_data)

    pynvml.nvmlShutdown()

    # Save to JSON file under this server's folder
    with open(os.path.join(SAVE_PATH, "gpu_stats.json"), "w") as f:
        json.dump(gpu_data, f, indent=4)

if __name__ == "__main__":
    while True:
        save_gpu_stats()
        time.sleep(2)  # Update every 5 seconds
