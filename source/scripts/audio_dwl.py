import os
import requests
import argparse

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_session_id_from_url(url):
    # Assuming the session ID is the last part of the URL, modify as needed
    return url.split('/')[-1]

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
        print(f'Downloaded: {filename}')
    else:
        print(f'Failed to download: {filename}, Status code: {response.status_code}')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Download audio files from Panopto URLs.')
    parser.add_argument('-t', '--token', required=True, help='OAuth access token')
    parser.add_argument('-f', '--file', required=True, help='File path to the text file with video URLs')
    parser.add_argument('-d', '--directory', default='Videos_DL', help='Directory to save audio files')
    return parser.parse_args()

def main():
    args = parse_arguments()
    ensure_directory_exists(args.directory)

    with open(args.file, 'r') as file:
        for url in file:
            url = url.strip()
            session_id = get_session_id_from_url(url)
            download_url = get_audio_download_url(session_id, args.token)
            if download_url:
                identification_code = session_id[:8]  # Adjust slice as needed
                filename = f'{identification_code}_audio.mp4'
                download_audio(download_url, args.directory, filename)
            else:
                print(f'No download URL found for {url}')

if __name__ == '__main__':
    main()
