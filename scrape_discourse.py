import requests
import json
import time
from pathlib import Path

# Base URLs
DISCOURSE_BASE = "https://forum.cursor.com"
CATEGORY_URL = f"{DISCOURSE_BASE}/c/bug-report/6/l/top.json"
TOPIC_URL = f"{DISCOURSE_BASE}/t"

def get_topics_page(page, per_page=2):
    """Fetch a page of topics from the bug report category"""
    params = {
        'filter': 'default',
        'page': page,
        'per_page': per_page,
        'period': 'all'
    }
    response = requests.get(CATEGORY_URL, params=params)
    return response.json()

def get_topic_discussion(slug):
    """Fetch full discussion data for a topic"""
    response = requests.get(f"{TOPIC_URL}/{slug}.json")
    return response.json()

def scrape_discussions(num_pages=10, per_page=2):
    """Scrape discussions from multiple pages and combine them"""
    all_discussions = []
    
    for page in range(num_pages):
        print(f"Fetching page {page}...")
        
        # Get topics list for current page
        topics_data = get_topics_page(page, per_page)
        
        if 'topic_list' not in topics_data or 'topics' not in topics_data['topic_list']:
            print(f"No topics found on page {page}")
            continue
            
        # Process each topic
        for topic in topics_data['topic_list']['topics']:
            slug = topic['slug']
            print(f"Fetching discussion for: {slug}")
            
            try:
                # Get full discussion data
                discussion = get_topic_discussion(slug)
                all_discussions.append(discussion)
                
                # Be nice to the server
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error fetching discussion for {slug}: {e}")
    
    return all_discussions

def main():
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    # Scrape discussions
    print("Starting scraping process...")
    discussions = scrape_discussions()
    
    # Write combined data to file
    output_file = "data/bug_report_small.json"
    print(f"Writing data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"discussions": discussions}, f, indent=2)
    
    print("Scraping completed!")

if __name__ == "__main__":
    main() 