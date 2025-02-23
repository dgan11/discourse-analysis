"""
--- Configuration Settings ---
# Set these values before running the script
# discourse starts at 0 and go to the first page
# number that returns null
"""

CATEGORY = "feedback"  # Options: "bug-report" or "feedback"
PAGE_COUNT = 2 
PAGE_SIZE = 10     
MAX_RETRIES = 3  # Number of retries for failed fetches
RETRY_DELAY = 2  # Seconds between retries

# CATEGORY_MAP = {
#     6: 'bug-report',
#     5: 'feature-request',
#     4: 'general',
#     7: 'feedback',
#     8: 'help'
# }
# ---------------------------

import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Base URLs
DISCOURSE_BASE = "https://forum.cursor.com"

# Define categories with their IDs
CATEGORIES = {
    "bug-report": 6,
    "feedback": 7
}

def get_category_url(category):
    """Generate category URL based on category name"""
    category_id = CATEGORIES.get(category)
    if not category_id:
        raise ValueError(f"Unknown category: {category}")
    return f"{DISCOURSE_BASE}/c/{category}/{category_id}/l/top.json"

def get_topics_page(category, page, per_page=PAGE_SIZE):
    """Fetch a page of topics from the specified category"""
    params = {
        'filter': 'default',
        'page': page,
        'per_page': per_page,
        'period': 'all'
    }
    category_url = get_category_url(category)
    response = requests.get(category_url, params=params)
    return response.json()

def get_topic_discussion(slug: str, retries: int = MAX_RETRIES) -> Tuple[dict, bool]:
    """
    Fetch full discussion data for a topic with retries
    Returns: (discussion_data, success)
    """
    for attempt in range(retries):
        try:
            response = requests.get(f"{DISCOURSE_BASE}/t/{slug}.json")
            response.raise_for_status()
            return response.json(), True
        except Exception as e:
            if attempt < retries - 1:
                print(f" - attempt {attempt + 1} failed for {slug}: {e}")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ All retries failed for {slug}: {e}")
                return None, False

def save_failed_slugs(failed_slugs: List[str], category: str):
    """Save failed slugs to a JSON file"""
    timestamp = time.strftime("%Y_%m_%d_%H:%M")
    failed_file = Path("data") / f"failed_slugs_{category}_{timestamp}.json"
    
    with open(failed_file, 'w', encoding='utf-8') as f:
        json.dump({"failed_slugs": failed_slugs, "category": category}, f, indent=2)
    
    print(f"Saved {len(failed_slugs)} failed slugs to {failed_file}")

def scrape_discussions(category=CATEGORY, num_pages=PAGE_COUNT, per_page=PAGE_SIZE):
    """Scrape discussions from multiple pages and combine them"""
    all_discussions = []
    failed_slugs = []
    
    for page in range(num_pages):
        print(f"Fetching page {page} from category '{category}'...")
        
        # Get topics list for current page
        topics_data = get_topics_page(category, page, per_page)
        
        if 'topic_list' not in topics_data or 'topics' not in topics_data['topic_list']:
            print(f"No topics found on page {page}")
            continue
            
        # Process each topic
        for topic in topics_data['topic_list']['topics']:
            slug = topic['slug']
            print(f"{slug}")
            
            discussion, success = get_topic_discussion(slug)
            if success:
                all_discussions.append(discussion)
            else:
                failed_slugs.append(slug)
            
            # Be nice to the server
            time.sleep(0.1)
    
    # Save failed slugs if any
    if failed_slugs:
        save_failed_slugs(failed_slugs, category)
    
    return all_discussions

def main():
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    # Get current timestamp for file suffix
    timestamp = time.strftime("%Y_%m_%d_%H:%M")
    
    # Scrape single category
    print(f"\n ⏰ Starting scraping process for {CATEGORY}...")
    discussions = scrape_discussions()
    
    # Write category data to file
    output_file = f"data/{CATEGORY}_{timestamp}.json"
    print(f"Writing data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"discussions": discussions}, f, indent=2)
    
    print(f"✅ Completed scraping {CATEGORY}!")

if __name__ == "__main__":
    main() 