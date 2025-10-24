# Set of methods to extract and validate input JSON files

import json
import pathlib

def extract_input_json(file_path:str) -> dict:
    if validate_file_path(file_path):
        with open(file_path, 'r') as f:
            input_json = json.load(f)
        return input_json

def validate_file_path(file_path:str) -> bool:
    if not file_exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path_endswith_json(file_path):
        raise ValueError(f"File is not a JSON file: {file_path}")
    
    return True

def path_endswith_json(file_path:str) -> bool:
    if file_path.lower().endswith('.json'): return True
    return False

def get_file_extension(file_path:str) -> str:
    path = pathlib.Path(file_path)
    return path.suffix

def file_exists(file_path:str) -> bool:
    path = pathlib.Path(file_path)
    return path.exists()

if __name__ == "__main__":
    file_path = '/home/ernestfoo/Documents/python-mailmerge/Sample_Input/zones.json'
    json_data = extract_input_json(file_path)
    print(type(json_data).__name__)
    print(json_data)