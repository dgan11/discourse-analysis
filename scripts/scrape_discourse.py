"""
--- Configuration Settings ---
# Set these values before running the script
# discourse starts at 0 and go to the first page
# number that returns null
"""
import asyncio
import aiohttp
import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime, timedelta
import hashlib
import pickle

# Configuration
CATEGORY = "how-to"  # Options: "bug-report" or "feedback"
PAGE_COUNT = 8
PAGE_SIZE = 100     
MAX_RETRIES = 3  # Number of retries for failed fetches
RETRY_DELAY = 2  # Seconds between retries

# Rate Limiting configurations so Discourse doesn't block us
RATE_LIMIT = 2  # requests per second
BATCH_SIZE = 2  # Number of concurrent requests
USE_CACHE = False  # Set to False to disable caching

# Base URLs and Categories
DISCOURSE_BASE = "https://forum.cursor.com"
CATEGORIES = {
    "site-feedback": 2, # 1 page ✔️
    "general": 4, # 44 pages | "discussion" on discourse
    "feature-requests": 5, # 12 pages
    "bug-report": 6, #28 pages
    "feedback": 7, #3 pages ✔️
    "how-to": 8, # 8 pages ✔️
    "showcase": 9, # 1 page ✔️
    "announcements": 11, # 1 page ✔️
}

"""
Details:
-  async processing (aiohttp)
  - multiple concurrent requests instead of synchronous request
- batch processing in batches of 5
- cache to avoid redundant fetches (store 24 hours in `cache` directory locally)
- connection pooling & rate limiting
  - controlled rate limiting
"""

class Cache:
    def __init__(self, cache_dir="cache", expire_after=timedelta(hours=24)):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.expire_after = expire_after
    
    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.pickle"
    
    async def get_or_fetch(self, session: aiohttp.ClientSession, url: str, **kwargs) -> dict:
        """Get from cache or fetch and cache"""
        cache_path = self._get_cache_path(url)
        
        # Check cache if enabled
        if USE_CACHE and cache_path.exists():
            with open(cache_path, 'rb') as f:
                timestamp, data = pickle.load(f)
                if datetime.now() - timestamp < self.expire_after:
                    print(f"Cache hit for {url}")
                    return data
        
        # Fetch and cache
        print(f"Fetching {url}")
        async with session.get(url, **kwargs) as response:
            data = await response.json()
            if USE_CACHE:  # Only cache if enabled
                with open(cache_path, 'wb') as f:
                    pickle.dump((datetime.now(), data), f)
            return data

# Initialize cache
cache = Cache()

def get_category_url(category):
    """Generate category URL based on category name"""
    category_id = CATEGORIES.get(category)
    if not category_id:
        raise ValueError(f"Unknown category: {category}")
    return f"{DISCOURSE_BASE}/c/{category}/{category_id}/l/top.json"

async def get_topic_discussion_async(session: aiohttp.ClientSession, slug: str, retries: int = MAX_RETRIES) -> Tuple[dict, bool]:
    """Async version of get_topic_discussion"""
    url = f"{DISCOURSE_BASE}/t/{slug}.json"
    
    for attempt in range(retries):
        try:
            data = await cache.get_or_fetch(session, url)
            return data, True
        except Exception as e:
            if attempt < retries - 1:
                print(f" - attempt {attempt + 1} failed for {slug}: {e}")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"❌ All retries failed for {slug}: {e}")
                return None, False

async def scrape_discussions_async(category=CATEGORY, num_pages=PAGE_COUNT, per_page=PAGE_SIZE):
    """Async version of scrape_discussions"""
    all_discussions = []
    failed_slugs = []
    
    # Configure connection pooling
    conn = aiohttp.TCPConnector(limit=RATE_LIMIT)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
        # First get all topics from all pages
        topics = []
        for page in range(num_pages):
            params = {
                'filter': 'default',
                'page': page,
                'per_page': per_page,
                'period': 'all'
            }
            category_url = get_category_url(category)
            try:
                data = await cache.get_or_fetch(session, category_url, params=params)
                if 'topic_list' in data and 'topics' in data['topic_list']:
                    topics.extend(data['topic_list']['topics'])
                    print(f"Found {len(data['topic_list']['topics'])} topics on page {page}")
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
        
        # Process topics in batches
        for i in range(0, len(topics), BATCH_SIZE):
            batch = topics[i:i + BATCH_SIZE]
            print(f"Processing batch {i//BATCH_SIZE + 1}/{len(topics)//BATCH_SIZE + 1}")
            
            # Create tasks for the batch
            tasks = []
            for topic in batch:
                tasks.append(get_topic_discussion_async(session, topic['slug']))
            
            # Wait for small delay between batches
            await asyncio.sleep(1/RATE_LIMIT)
            
            # Process batch
            results = await asyncio.gather(*tasks)
            for (result, success), topic in zip(results, batch):
                if success:
                    all_discussions.append(result)
                else:
                    failed_slugs.append(topic['slug'])
    
    return all_discussions, failed_slugs

def save_failed_slugs(failed_slugs: List[str], category: str):
    """Save failed slugs to a JSON file"""
    timestamp = time.strftime("%Y_%m_%d_%H:%M")
    failed_file = Path("data") / f"failed_slugs_{category}_{timestamp}.json"
    
    with open(failed_file, 'w', encoding='utf-8') as f:
        json.dump({"failed_slugs": failed_slugs, "category": category}, f, indent=2)
    
    print(f"Saved {len(failed_slugs)} failed slugs to {failed_file}")

async def main_async():
    """Async main function"""
    Path("data").mkdir(exist_ok=True)
    timestamp = time.strftime("%Y_%m_%d_%H:%M")
    
    print(f"\n ⏰ Starting scraping process for {CATEGORY}...")
    discussions, failed_slugs = await scrape_discussions_async()
    
    # Save results
    output_file = f"data/{CATEGORY}_{timestamp}.json"
    print(f"Writing data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"discussions": discussions}, f, indent=2)
    
    if failed_slugs:
        save_failed_slugs(failed_slugs, CATEGORY)
    
    print(f"✅ Completed scraping {CATEGORY}!")
    print(f"Successfully scraped {len(discussions)} discussions")
    print(f"Failed to scrape {len(failed_slugs)} discussions")

if __name__ == "__main__":
    asyncio.run(main_async())