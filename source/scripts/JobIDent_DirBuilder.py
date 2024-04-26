import os
import json

def find_json_file(directory):
    # Search for the first JSON file in the specified directory
    for file in os.listdir(directory):
        if file.endswith(".json"):
            return os.path.join(directory, file)
    return None

def create_directory_from_json(json_path):
    # Read the JSON file
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    job_ident = data['JobIDent']
    directory_path = f"/tmp/{job_ident}"
    
    # Create the directory
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory created at {directory_path}")
    else:
        print(f"Directory already exists at {directory_path}")
    
    return directory_path

def main():
    # Define the directory where JSON files are expected to be found
    json_directory = '/tmp'
    
    # Find the first JSON file in the directory
    json_path = find_json_file(json_directory)
    
    if json_path:
        # Create directory based on the JobIDent
        directory_path = create_directory_from_json(json_path)
        print(f"Processed directory: {directory_path}")
    else:
        print("No JSON file found in the directory.")

if __name__ == "__main__":
    main()
