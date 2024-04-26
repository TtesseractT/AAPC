import json
import requests
import argparse

def validate_urls(urls_file, api_key, output_path):
    results = {}
    with open(urls_file, 'r') as file:
        for url in file:
            url = url.strip()
            valid = check_url_validity(url, api_key)
            results[url] = valid
    
    # Save results to JSON file
    output_file = f'{output_path}/failed_links.json'
    with open(output_file, 'w') as f:
        json.dump({k: v for k, v in results.items() if not v}, f)
    
    return all(results.values())

def check_url_validity(url, api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    # Simulated API endpoint for checking video existence
    # This endpoint and logic should be adapted to the actual API you're using
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def parse_arguments():
    parser = argparse.ArgumentParser(description='Validate URLs for video references.')
    parser.add_argument('-f', '--file', required=True, help='File path to the text file with URLs')
    parser.add_argument('-k', '--apikey', required=True, help='Panopto API Key')
    parser.add_argument('-o', '--output', required=True, help='Output directory to save the JSON file')
    return parser.parse_args()

def main():
    args = parse_arguments()
    all_valid = validate_urls(args.file, args.apikey, args.output)
    
    print(f"All URLs valid: {all_valid}")

if __name__ == '__main__':
    main()
