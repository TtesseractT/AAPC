import hashlib
import json
import argparse
from datetime import datetime

def generate_job_identifier(input_string, salt):
    # Create a hash object with SHA256
    hash_obj = hashlib.sha256()
    
    # Update hash object with input and salt
    input_bytes = input_string.encode()
    salt_bytes = salt.encode()
    hash_obj.update(input_bytes + salt_bytes)
    
    # Get the hexadecimal digest and slice the first 20 characters
    hex_digest = hash_obj.hexdigest()[:20]
    
    return hex_digest

def save_to_json(job_ident, file_path):
    # Data to save
    data = {"JobIDent": job_ident}
    
    # Write data to a JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file)
    
    return file_path

def get_current_datetime():
    # Get current date and time formatted as 'HH:MM:SS DD/MM/YYYY'
    return datetime.now().strftime("%H:%M:%S %d/%m/%Y")

def main():
    parser = argparse.ArgumentParser(description="Generate a unique 20 character hex number using SHA with salt.")
    parser.add_argument('-i', '--input', type=str, help="Optional input date & time string, e.g., '12:00:00 01/01/2024'. Uses current system date and time if omitted.")
    parser.add_argument('-s', '--salt', type=str, help="Optional salt string. Defaults to the input string if omitted.")
    parser.add_argument('-f', '--filepath', type=str, required=True, help="Full path to save the resulting JSON file.")
    
    args = parser.parse_args()

    # If no input string is provided, use the current system date and time
    if not args.input:
        args.input = get_current_datetime()
    
    # If no salt is provided, use the input string
    if not args.salt:
        args.salt = args.input
    
    # Generate the Job Identifier
    job_ident = generate_job_identifier(args.input, args.salt)
    
    # Save the Job Identifier to a JSON file
    result_path = save_to_json(job_ident, args.filepath)
    
    #print(f"Job Identifier has been saved to {result_path}")

if __name__ == "__main__":
    main()
