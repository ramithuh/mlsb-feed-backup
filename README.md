# MLSB Feed GitHub Pages Backup

This directory contains a **static backup solution** for the MLSB (Machine Learning in Structural Biology) Bluesky feed generator.

## Purpose

During server downtime, this backup serves historical posts via GitHub Pages, ensuring continuity for Bluesky users.

## Architecture

**Normal Operation**: Live Flask server with real-time AT Protocol integration
**Downtime**: Static GitHub Pages serving historical posts from database export

## Files

- `export_feed.py` - Exports historical posts from `feed_database2.db` to static JSON files
- `_site/` - Generated static files (AT Protocol endpoints)

## Generated Endpoints

Following the blog post's proven format:

```
_site/
├── .well-known/did.json
├── xrpc/app.bsky.feed.describeFeedGenerator/index.json
└── xrpc/app.bsky.feed.getFeedSkeleton/index.json
```

## How It Works

1. **Export**: `export_feed.py` reads your curated posts from the database
2. **Format**: Generates JSON files matching the blog post's serving structure  
3. **Deploy**: Push static files to GitHub repository once
4. **Failover**: During downtime, update DNS to point to GitHub Pages

## Setup Instructions

### 1. Generate Static Backup (Before Downtime)
```bash
# Run locally to generate static files (can run from any directory)
cd backup_solution
source ~/miniconda3/etc/profile.d/conda.sh && conda activate bluesky
export HOSTNAME="mlsb.ramith.io"
export WHATS_ALF_URI="at://did:plc:57azw27ix6arhpw6lmkunmp7/app.bsky.feed.generator/MLSB"
python export_feed.py
```

### 2. Create GitHub Repository & Deploy
```bash
# Create new repo for backup
gh repo create mlsb-feed-backup --public

# Initialize and push from backup_solution directory
cd backup_solution
git init
git add .
git commit -m "MLSB feed static backup"
git remote add origin https://github.com/yourusername/mlsb-feed-backup.git
git push -u origin master

# Add the generated _site directory with all the static files
git add _site/
git commit -m "Add generated static site files"
git push origin master
```

### 3. Enable GitHub Pages
- Go to repository Settings → Pages  
- Source: "Deploy from a branch"
- Branch: `master` (or whatever branch you pushed to)
- Folder: `/_site` (this is where your AT Protocol endpoints are)
- Custom domain: (Optional) Set your backup domain

**That's it!** No GitHub Actions, no secrets, no periodic updates needed.

## Failover Process

**When Your Server Goes Down:**
1. Update DNS A record to point to GitHub Pages IP
2. Or update DID document serviceEndpoint to GitHub Pages URL
3. Bluesky clients automatically fetch from static backup
4. Users see historical posts (better than no posts!)

**When Server Comes Back:**
1. Revert DNS changes
2. Live server takes over with real-time updates

## Benefits

- ✅ **Zero Cost**: Free GitHub Pages hosting
- ✅ **Reliable**: GitHub's uptime >> local server
- ✅ **Simple**: One-time manual setup, no automation complexity
- ✅ **Historical**: Preserves all your curated ML/Bio posts
- ✅ **Seamless**: Same AT Protocol endpoints as live server
- ✅ **Proven**: Based on working blog post implementation