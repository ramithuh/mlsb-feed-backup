# MLSB Feed Backup

Static backup of the MLSB (Machine Learning in Structural Biology) Bluesky feed.

**Generated**: 2025-07-23T07:35:45.877570
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
