#!/usr/bin/env python3
"""
Test script for downloading book covers from Open Library
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'image_processing'))

from downloader import fetch_and_download_covers


def main():
    print("=" * 60)
    print("Testing Book Cover Downloader from Open Library")
    print("=" * 60)
    
    # Test with different queries
    queries = [
        ("classic literature", 5),
        ("science fiction", 3),
        ("python programming", 2),
    ]
    
    for query, num_books in queries:
        print(f"\n\nDownloading {num_books} covers for: '{query}'")
        print("-" * 60)
        
        files = fetch_and_download_covers(query=query, num_books=num_books)
        
        print(f"\nDownloaded {len(files)} covers:")
        for file_path in files:
            file_size = os.path.getsize(file_path)
            print(f"  ✓ {os.path.basename(file_path)} ({file_size:,} bytes)")
    
    print("\n" + "=" * 60)
    print("Download test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()