"""
Script to refetch previously failed Discourse discussions
"""

import json
import time
from pathlib import Path
from typing import List, Dict
import requests

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2
DISCOURSE_BASE = "https://forum.cursor.com"

def get_topic_discussion(slug: str, retries: int = MAX_RETRIES):
    """Fetch full discussion data for a topic with retries"""
    for attempt in range(retries):
        try:
            response = requests.get(f"{DISCOURSE_BASE}/t/{slug}.json")
            response.raise_for_status()
            return response.json(), True
        except Exception as e:
            if attempt < retries - 1:
                print(f"Attempt {attempt + 1} failed for {slug}: {e}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ All retries failed for {slug}: {e}")
                return None, False

def load_failed_slugs(failed_file: str) -> Dict:
    """Load failed slugs from JSON file"""
    with open(failed_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Get list of failed slug files
    data_dir = Path("data")
    failed_files = list(data_dir.glob("failed_slugs_*.json"))
    
    if not failed_files:
        print("No failed slug files found in data directory!")
        return
    
    print(f"Found {len(failed_files)} failed slug files")
    
    # Process each file
    for failed_file in failed_files:
        print(f"\nProcessing {failed_file}...")
        
        # Load failed slugs
        data = load_failed_slugs(failed_file)
        category = data['category']
        failed_slugs = data['failed_slugs']
        
        if not failed_slugs:
            print("No failed slugs in file")
            continue
            
        print(f"Attempting to refetch {len(failed_slugs)} failed discussions...")
        
        # Try to fetch each failed slug
        successful_discussions = []
        still_failed = []
        
        for slug in failed_slugs:
            print(f"Refetching: {slug}")
            discussion, success = get_topic_discussion(slug)
            
            if success:
                successful_discussions.append(discussion)
            else:
                still_failed.append(slug)
            
            time.sleep(1)  # Be nice to the server
        
        # Save results
        if successful_discussions:
            timestamp = time.strftime("%Y_%m_%d_%H:%M")
            output_file = data_dir / f"{category}_refetched_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"discussions": successful_discussions}, f, indent=2)
            
            print(f"✅ Saved {len(successful_discussions)} refetched discussions to {output_file}")
        
        # Save any remaining failed slugs
        if still_failed:
            timestamp = time.strftime("%Y_%m_%d_%H:%M")
            new_failed_file = data_dir / f"failed_slugs_{category}_{timestamp}.json"
            
            with open(new_failed_file, 'w', encoding='utf-8') as f:
                json.dump({"failed_slugs": still_failed, "category": category}, f, indent=2)
            
            print(f"❌ {len(still_failed)} slugs still failed, saved to {new_failed_file}")

if __name__ == "__main__":
    main() 