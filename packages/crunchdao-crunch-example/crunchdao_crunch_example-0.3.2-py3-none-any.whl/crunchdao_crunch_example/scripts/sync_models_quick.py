#!/usr/bin/env python3
"""
Quick sync script for models - updates only changed files
"""

import os
import shutil
from pathlib import Path

def quick_sync():
    """Quick sync - only copy if source is newer"""
    # Go up to package root and find models
    package_root = Path(__file__).parent.parent
    source_dir = package_root / "models"
    target_dir = Path("/Users/boris/projects/crunch/models-orchestrator/storage")
    
    print(f"Quick sync: {source_dir} -> {target_dir}")
    
    updated_count = 0
    
    for model_dir in source_dir.iterdir():
        if model_dir.is_dir():
            model_name = model_dir.name
            
            # Check resources
            source_resources = model_dir / "resources"
            target_resources = target_dir / model_name / "resources"
            
            if source_resources.exists():
                for file in source_resources.rglob("*"):
                    if file.is_file():
                        rel_path = file.relative_to(source_resources)
                        target_file = target_resources / rel_path
                        
                        # Copy if target doesn't exist or source is newer
                        if not target_file.exists() or file.stat().st_mtime > target_file.stat().st_mtime:
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file, target_file)
                            print(f"Updated: {model_name}/resources/{rel_path}")
                            updated_count += 1
            
            # Check submissions
            source_submissions = model_dir / "submissions"
            target_submissions = target_dir / model_name / "submissions"
            
            if source_submissions.exists():
                for file in source_submissions.rglob("*"):
                    if file.is_file() and not file.name.endswith('.pyc'):  # Skip compiled Python files
                        rel_path = file.relative_to(source_submissions)
                        target_file = target_submissions / rel_path
                        
                        # Copy if target doesn't exist or source is newer
                        if not target_file.exists() or file.stat().st_mtime > target_file.stat().st_mtime:
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file, target_file)
                            print(f"Updated: {model_name}/submissions/{rel_path}")
                            updated_count += 1
    
    if updated_count == 0:
        print("✓ All files are up to date!")
    else:
        print(f"✓ Updated {updated_count} files")

if __name__ == "__main__":
    quick_sync()