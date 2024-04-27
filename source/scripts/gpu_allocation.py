import os
import subprocess
import time
from multiprocessing import Pool, Manager, Lock

def process_file(args):
    file, gpu_id, queue_dict, lock = args
    input_file = os.path.join(input_folder, file)
    output_folder = os.path.join(destination_folder, file.split('.')[0])
    os.makedirs(output_folder, exist_ok=True)
    
    with lock:
        queue_dict[gpu_id] += 1

    try:
        # Run the subprocess command
        subprocess.run(['whisper', input_file, "flag information here"], cwd=output_folder)
    finally:
        with lock:
            queue_dict[gpu_id] -= 1

def gpu_allocator(queue_dict, lock):
    while True:
        with lock:
            for gpu_id, count in queue_dict.items():
                if count < max_jobs_per_gpu:
                    return gpu_id
        time.sleep(0.5)  # Sleep for 500ms before checking again

if __name__ == "__main__":
    input_folder = 'path_to_input_folder'
    destination_folder = 'path_to_destination_folder'
    max_jobs_per_gpu = 8
    num_gpus = 4
    
    manager = Manager()
    queue_dict = manager.dict({i: 0 for i in range(num_gpus)})
    lock = Lock()

    # List all files in the input directory
    files = [f for f in os.listdir(input_folder) if f.endswith('.wav')]

    with Pool(num_gpus * max_jobs_per_gpu) as pool:
        pool.map(process_file, [(file, gpu_allocator(queue_dict, lock), queue_dict, lock) for file in files])

    # Move original MP4 and WAV files to destination
    for file in files:
        original_mp4 = os.path.join(input_folder, file.replace('.wav', '.mp4'))
        original_wav = os.path.join(input_folder, file)
        subprocess.run(['mv', original_mp4, destination_folder])
        subprocess.run(['mv', original_wav, destination_folder])
