import json
from pathlib import Path
import sys

def validate_json_file(file_path):
    """Validate a JSON file and count discussions"""
    print(f"\nValidating: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if 'discussions' not in data:
            print("❌ Error: No 'discussions' array found in JSON!")
            return
            
        discussion_count = len(data['discussions'])
        print(f"✅ Found {discussion_count} discussions")
        
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    # If file provided as argument, use that
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if file_path.exists():
            validate_json_file(file_path)
        else:
            print(f"❌ File not found: {file_path}")
        return
    
    # Otherwise, look in data directory
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ No data directory found!")
        return
        
    # Find all JSON files
    json_files = list(data_dir.glob('*.json'))
    
    if not json_files:
        print("❌ No JSON files found in data directory!")
        return
        
    # Validate each file
    for file_path in json_files:
        validate_json_file(file_path)

if __name__ == "__main__":
    main()