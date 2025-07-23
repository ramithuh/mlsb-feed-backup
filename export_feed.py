#!/usr/bin/env python3
"""
Export MLSB feed data to static JSON files for GitHub Pages backup
Following the blog post's serving format: https://amitness.com/posts/bluesky-custom-feed/
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import server modules
# and change working directory to project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

from server.database import Post, db
from server import config

# Configuration matching blog post approach
OUTPUT_DIR = "_site"
STICKY_POSTS = [
    "at://did:plc:a33wx75tk3vfmbqb6brpbxo4/app.bsky.feed.post/3leve7zx2zk2r",
    "at://did:plc:a33wx75tk3vfmbqb6brpbxo4/app.bsky.feed.post/3lulf4zaacc2o"
]

def ensure_dirs():
    """Create necessary directory structure"""
    dirs = [
        f"{OUTPUT_DIR}/.well-known",
        f"{OUTPUT_DIR}/xrpc/app.bsky.feed.getFeedSkeleton", 
        f"{OUTPUT_DIR}/xrpc/app.bsky.feed.describeFeedGenerator"
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def export_did_json():
    """Export DID document for service identity"""
    did_data = {
        '@context': ['https://www.w3.org/ns/did/v1'],
        'id': config.SERVICE_DID,
        'service': [
            {
                'id': '#bsky_fg',
                'type': 'BskyFeedGenerator',
                'serviceEndpoint': f'https://{config.HOSTNAME}'
            }
        ]
    }
    
    with open(f"{OUTPUT_DIR}/.well-known/did.json", 'w') as f:
        json.dump(did_data, f, indent=2)

def export_feed_description():
    """Export feed generator description"""
    description_data = {
        'encoding': 'application/json',
        'body': {
            'did': config.SERVICE_DID,
            'feeds': [{'uri': config.WHATS_ALF_URI}]
        }
    }
    
    with open(f"{OUTPUT_DIR}/xrpc/app.bsky.feed.describeFeedGenerator/index.json", 'w') as f:
        json.dump(description_data, f, indent=2)

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def export_feed_skeleton():
    """Export feed data in blog post's exact format"""
    print("Fetching posts from database...")
    
    # Get all posts ordered by most recent first (matching your live feed)
    posts = list(Post.select().order_by(Post.indexed_at.desc(), Post.cid.desc()))
    
    if not posts:
        print("No posts found in database")
        # Create empty feed matching blog post format
        feed_data = {"feed": [{"post": uri} for uri in STICKY_POSTS]}
    else:
        print(f"Found {len(posts)} posts")
        
        # Build feed items - blog post format (no pagination, just all posts)
        feed_items = []
        
        # Add sticky posts first (matching your live feed logic)
        feed_items.extend([{"post": uri} for uri in STICKY_POSTS])
        
        # Add all historical posts
        feed_items.extend([{"post": post.uri} for post in posts])
        
        # Create feed data matching blog post's format
        feed_data = {
            "feed": feed_items
        }
        # Note: No cursor field for static backup (blog post omits it when no pagination)
    
    # Save as index.json (blog post's main endpoint)
    filename = f"{OUTPUT_DIR}/xrpc/app.bsky.feed.getFeedSkeleton/index.json"
    with open(filename, 'w') as f:
        json.dump(feed_data, f, indent=2)
    
    print(f"  Created static feed with {len(feed_data['feed'])} total items")

def create_readme():
    """Create README for the backup solution"""
    readme_content = f"""# MLSB Feed Backup

Static backup of the MLSB (Machine Learning in Structural Biology) Bluesky feed.

**Generated**: {datetime.now().isoformat()}
**Purpose**: Provides historical feed data during server downtime

## Endpoints

- `/.well-known/did.json` - Service identity document
- `/xrpc/app.bsky.feed.describeFeedGenerator/` - Feed metadata
- `/xrpc/app.bsky.feed.getFeedSkeleton/` - Feed data

## Usage

This backup serves the same AT Protocol endpoints as the live server.
During server downtime, update your DNS to point to this GitHub Pages URL.

## Update Process

This is a one-time static snapshot of historical posts.
Generated manually before planned server downtime.
"""
    
    with open(f"{OUTPUT_DIR}/README.md", 'w') as f:
        f.write(readme_content)

def main():
    """Main export function"""
    print("Starting MLSB feed export...")
    
    # Ensure database connection (handle if already connected)
    try:
        db.connect()
    except Exception as e:
        if "already opened" in str(e):
            print("Database already connected, continuing...")
        else:
            raise
    
    # Create directory structure
    ensure_dirs()
    
    # Export all components
    export_did_json()
    export_feed_description() 
    export_feed_skeleton()
    create_readme()
    
    print("Export completed successfully!")
    print(f"Files saved to: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("1. Commit and push these files to GitHub")
    print("2. Enable GitHub Pages on the repository (source: _site directory)")
    print("3. During downtime, update DNS to point to GitHub Pages")

if __name__ == "__main__":
    main()