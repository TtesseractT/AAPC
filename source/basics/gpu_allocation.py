import os
import subprocess
import time
from multiprocessing import Pool, Manager, Lock
import argparse

def process_file(args):
    file, output_folder, gpu_id, queue_dict, lock = args
    os.chdir(output_folder)  # Change current working directory to the output directory

    with lock:
        queue_dict[gpu_id] += 1

    try:
        # Run the subprocess command within the output directory
        subprocess.run(f'whisper "{file}" --device cuda --model large --language en --task transcribe --output_format all', shell=True)
    finally:
        os.chdir('..')  # Change back to the parent directory
        with lock:
            queue_dict[gpu_id] -= 1

def prepare_directories(files, input_folder, destination_folder):
    paths = []
    for file in files:
        output_folder = os.path.join(destination_folder, file.split('.')[0])
        os.makedirs(output_folder, exist_ok=True)
        paths.append((file, output_folder))
    return paths

def gpu_allocator(queue_dict, lock):
    while True:
        with lock:
            for gpu_id, count in queue_dict.items():
                if count < max_jobs_per_gpu:
                    return gpu_id
        time.sleep(0.5)  # Sleep for 500ms before checking again

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Whisper GPU transcription")
    parser.add_argument('-i', '--input', type=str, required=True, help="Input folder")
    parser.add_argument('-d', '--dir', type=str, required=True, help="Destination folder")
    parser.add_argument('-g', '--maxj', type=int, required=True, help="Maximum jobs per GPU")
    parser.add_argument('-v', '--maxg', type=int, required=True, help="Total GPUs available")
    args = parser.parse_args()

    input_folder = args.input
    destination_folder = args.dir
    max_jobs_per_gpu = args.maxj
    num_gpus = args.maxg
    
    manager = Manager()
    queue_dict = manager.dict({i: 0 for i in range(num_gpus)})
    lock = Lock()

    # List all files in the input directory and prepare directories
    files = [f for f in os.listdir(input_folder) if f.endswith('.wav')]
    prepared_paths = prepare_directories(files, input_folder, destination_folder)

    with Pool(num_gpus * max_jobs_per_gpu) as pool:
        pool.map(process_file, [(os.path.join(input_folder, f), d, gpu_allocator(queue_dict, lock), queue_dict, lock) for f, d in prepared_paths])

    # Move original MP4 and WAV files to destination
    for file in files:
        original_mp4 = os.path.join(input_folder, file.replace('.wav', '.mp4'))
        original_wav = os.path.join(input_folder, file)
        subprocess.run(['mv', original_mp4, destination_folder])
        subprocess.run(['mv', original_wav, destination_folder])
