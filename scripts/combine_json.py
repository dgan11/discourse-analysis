"""
--- Configuration Settings ---
# Set these values before running the script
"""

FILE_PREFIX = "med"  # Prefix for files to combine
# ---------------------------

import json
from pathlib import Path
import time

def combine_json_files(input_files):
    """Combine multiple JSON files with discussions arrays into one"""
    all_discussions = []
    
    for file_path in input_files:
        print(f"Reading {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_discussions.extend(data['discussions'])
    
    return {"discussions": all_discussions}

def main():
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Get current timestamp
    timestamp = time.strftime("%Y_%m_%d_%H:%M")
    
    # Find all JSON files in data directory that start with the prefix
    json_files = list(data_dir.glob(f'{FILE_PREFIX}*.json'))
    
    if not json_files:
        print(f"No {FILE_PREFIX}* JSON files found in data directory!")
        return
        
    print(f"Found {len(json_files)} {FILE_PREFIX}* files to combine")
    
    # Combine the files
    combined_data = combine_json_files(json_files)
    
    # Write combined data
    output_file = data_dir / f"{FILE_PREFIX}_full_data_{timestamp}.json"
    print(f"Writing combined data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2)
    
    print(f"Successfully combined {len(combined_data['discussions'])} discussions!")

if __name__ == "__main__":
    main()