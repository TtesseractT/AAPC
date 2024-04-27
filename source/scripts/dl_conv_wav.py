import os
import requests
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from tqdm import tqdm

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_session_id_from_url(url):
    return url.split('/')[-1]  # Modify as needed based on URL structure

def get_audio_download_url(session_id, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    api_endpoint = f'https://yourinstitution.hosted.panopto.com/Panopto/api/v1/sessions/{session_id}/outputs'
    response = requests.get(api_endpoint, headers=headers)
    if response.status_code == 200:
        outputs = response.json()
        for output in outputs:
            if output['Type'] == 'AudioPodcast':
                return output['DownloadUrl']
    return None

def download_audio(download_url, directory, filename):
    response = requests.get(download_url)
    if response.status_code == 200:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return filename
    else:
        return None

def convert_to_wav(mp4_file, directory):
    wav_file = mp4_file.replace('.mp4', '.wav')
    input_path = os.path.join(directory, mp4_file)
    output_path = os.path.join(directory, 'WAV Files', wav_file)
    subprocess.run(['ffmpeg', '-i', input_path, output_path, '-loglevel', 'quiet'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return wav_file


def parse_arguments():
    parser = argparse.ArgumentParser(description='Download and convert audio files from Panopto URLs.')
    parser.add_argument('-t', '--token', required=True, help='OAuth access token')
    parser.add_argument('-f', '--file', required=True, help='File path to the text file with video URLs')
    parser.add_argument('-d', '--directory', default='Videos_DL', help='Directory to save audio files')
    return parser.parse_args()

def main():
    args = parse_arguments()
    ensure_directory_exists(args.directory)
    ensure_directory_exists(os.path.join(args.directory, 'WAV Files'))

    with open(args.file, 'r') as file:
        urls = file.read().splitlines()

    # Download using ThreadPoolExecutor
    with ThreadPoolExecutor(min(10, os.cpu_count())) as executor:
        download_results = list(tqdm(executor.map(lambda url: download_audio(get_audio_download_url(get_session_id_from_url(url), args.token), args.directory, url.split('/')[-1]), urls), total=len(urls)))


    # Convert downloaded MP4 to WAV using ProcessPoolExecutor
    mp4_files = [result for result in download_results if result is not None]
    with ProcessPoolExecutor(os.cpu_count()) as executor:
        list(tqdm(executor.map(lambda file: convert_to_wav(file, args.directory), mp4_files), total=len(mp4_files)))

if __name__ == '__main__':
    main()
