#!/usr/bin/env python3
"""
Script to clean up old files after reorganization.
"""

import os
import shutil
from pathlib import Path

def cleanup_old_files():
    """Remove old files that have been moved to new locations."""
    project_root = Path(__file__).parent.parent
    
    # Files that have been moved to scripts/
    old_files = [
        'debug_email.py',
        'test_pipeline.py', 
        'troubleshoot.py',
        'cli.py'
    ]
    
    # Documentation files that have been moved
    old_docs = [
        'QUICK_START.md'
    ]
    
    print("🧹 Cleaning up old files...")
    
    # Remove old script files from root
    for file in old_files:
        file_path = project_root / file
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✅ Removed: {file}")
            except Exception as e:
                print(f"❌ Failed to remove {file}: {e}")
    
    # Remove old documentation files from root
    for doc in old_docs:
        doc_path = project_root / doc
        if doc_path.exists():
            try:
                doc_path.unlink()
                print(f"✅ Removed: {doc}")
            except Exception as e:
                print(f"❌ Failed to remove {doc}: {e}")
    
    # Replace README.md with the new version
    old_readme = project_root / 'README.md'
    new_readme = project_root / 'README_NEW.md'
    
    if new_readme.exists():
        try:
            if old_readme.exists():
                old_readme.unlink()
            new_readme.rename(old_readme)
            print(f"✅ Updated README.md")
        except Exception as e:
            print(f"❌ Failed to update README.md: {e}")
    
    print("\n🎉 File cleanup completed!")

if __name__ == "__main__":
    cleanup_old_files()
