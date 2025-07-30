#!/usr/bin/env python3
"""
Sync models from iris example to models-orchestrator storage
"""

import os
import shutil
import sys
import subprocess
from pathlib import Path

def cleanup_docker():
    """Stop and remove crunchdao/model-runner containers and images"""
    print("\n=== Docker Cleanup ===")
    
    try:
        # Check if Docker is available
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Docker not available, skipping cleanup")
            return
        
        print("Docker found, proceeding with cleanup...")
        
        # Find and stop all containers using crunchdao/model-runner images
        print("Looking for containers using crunchdao/model-runner images...")
        
        # First get all crunchdao/model-runner image IDs
        image_result = subprocess.run([
            'docker', 'images', 'crunchdao/model-runner', '--format', '{{.ID}}'
        ], capture_output=True, text=True)
        
        image_ids = []
        if image_result.returncode == 0 and image_result.stdout.strip():
            image_ids = image_result.stdout.strip().split('\n')
        
        all_container_ids = []
        
        # For each image, find containers using it
        for image_id in image_ids:
            try:
                result = subprocess.run([
                    'docker', 'ps', '-a', '--filter', f'ancestor={image_id}', 
                    '--format', '{{.ID}} {{.Names}} {{.Status}}'
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    containers = result.stdout.strip().split('\n')
                    for container in containers:
                        print(f"  Found container: {container} (using image {image_id[:12]})")
                        all_container_ids.append(container.split()[0])
            except subprocess.CalledProcessError:
                continue
        
        # Also check by repository name
        try:
            result = subprocess.run([
                'docker', 'ps', '-a', '--filter', 'ancestor=crunchdao/model-runner', 
                '--format', '{{.ID}} {{.Names}} {{.Status}}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                containers = result.stdout.strip().split('\n')
                for container in containers:
                    container_id = container.split()[0]
                    if container_id not in all_container_ids:
                        print(f"  Found container: {container} (using crunchdao/model-runner)")
                        all_container_ids.append(container_id)
        except subprocess.CalledProcessError:
            pass
        
        if all_container_ids:
            print(f"Found {len(all_container_ids)} total containers to remove")
            
            # Stop containers
            print(f"Stopping containers...")
            try:
                subprocess.run(['docker', 'stop'] + all_container_ids, check=True)
                print(f"Stopped {len(all_container_ids)} containers")
            except subprocess.CalledProcessError as e:
                print(f"Some containers may already be stopped: {e}")
            
            # Remove containers individually
            print(f"Removing containers...")
            for container_id in all_container_ids:
                try:
                    result = subprocess.run(['docker', 'rm', '-f', container_id], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"  Removed container {container_id[:12]}")
                    else:
                        # Check if container is already gone
                        check_result = subprocess.run(['docker', 'ps', '-a', '-q', '--filter', f'id={container_id}'], 
                                                    capture_output=True, text=True)
                        if not check_result.stdout.strip():
                            print(f"  Container {container_id[:12]} already removed")
                        else:
                            print(f"  Could not remove container {container_id[:12]}: {result.stderr.strip()}")
                except subprocess.CalledProcessError as e:
                    print(f"  Error removing container {container_id[:12]}: {e}")
            
            print(f"Container removal process completed")
        else:
            print("No containers found using crunchdao/model-runner images")
        
        # Remove crunchdao/model-runner images
        print("Removing crunchdao/model-runner images...")
        try:
            # Get image IDs for crunchdao/model-runner
            result = subprocess.run([
                'docker', 'images', 'crunchdao/model-runner', '--format', '{{.ID}}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                image_ids = result.stdout.strip().split('\n')
                print(f"Found {len(image_ids)} images to remove: {image_ids}")
                
                # Force remove images
                subprocess.run(['docker', 'rmi', '-f'] + image_ids, check=True)
                print(f"Removed {len(image_ids)} images")
            else:
                print("No images found for crunchdao/model-runner")
                
        except subprocess.CalledProcessError as e:
            print(f"Error removing images: {e}")
        
        # Clean up dangling images and containers
        print("Cleaning up dangling resources...")
        try:
            subprocess.run(['docker', 'system', 'prune', '-f'], check=True)
            print("Docker system cleanup completed")
        except subprocess.CalledProcessError as e:
            print(f"Error during system cleanup: {e}")
            
    except Exception as e:
        print(f"Docker cleanup failed: {e}")

def sync_models():
    """Sync models to the models-orchestrator storage directory"""
    
    # Source directory (current iris models)
    script_dir = Path(__file__).parent
    source_dir = script_dir / "models"
    
    # Target directory (models-orchestrator storage)
    target_dir = Path("/Users/boris/projects/crunch/models-orchestrator/storage")
    
    print(f"Syncing models from: {source_dir}")
    print(f"Syncing models to: {target_dir}")
    
    # Check if source directory exists
    if not source_dir.exists():
        print(f"ERROR: Source directory does not exist: {source_dir}")
        return False
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Get list of model directories
    model_dirs = [d for d in source_dir.iterdir() if d.is_dir()]
    
    if not model_dirs:
        print("No model directories found in source")
        return False
    
    print(f"Found {len(model_dirs)} model directories: {[d.name for d in model_dirs]}")
    
    # Sync each model
    for model_dir in model_dirs:
        model_name = model_dir.name
        print(f"\n=== Syncing {model_name} ===")
        
        # Source paths
        source_resources = model_dir / "resources"
        source_submissions = model_dir / "submissions"
        
        # Target paths
        target_model_dir = target_dir / model_name
        target_resources = target_model_dir / "resources"
        target_submissions = target_model_dir / "submissions"
        
        # Create target model directory
        target_model_dir.mkdir(exist_ok=True)
        
        # Sync resources
        if source_resources.exists():
            if target_resources.exists():
                shutil.rmtree(target_resources)
            shutil.copytree(source_resources, target_resources)
            
            # List copied resources
            resource_files = list(target_resources.rglob("*"))
            resource_files = [f for f in resource_files if f.is_file()]
            print(f"  Copied {len(resource_files)} resource files:")
            for file in resource_files:
                rel_path = file.relative_to(target_resources)
                file_size = file.stat().st_size
                print(f"    - {rel_path} ({file_size:,} bytes)")
        else:
            print(f"  WARNING: No resources directory found for {model_name}")
        
        # Sync submissions
        if source_submissions.exists():
            if target_submissions.exists():
                shutil.rmtree(target_submissions)
            shutil.copytree(source_submissions, target_submissions)
            
            # List copied submissions
            submission_files = list(target_submissions.rglob("*"))
            submission_files = [f for f in submission_files if f.is_file()]
            print(f"  Copied {len(submission_files)} submission files:")
            for file in submission_files:
                rel_path = file.relative_to(target_submissions)
                file_size = file.stat().st_size
                print(f"    - {rel_path} ({file_size:,} bytes)")
        else:
            print(f"  WARNING: No submissions directory found for {model_name}")
    
    print(f"\n=== Sync completed successfully ===")
    print(f"All models synced to: {target_dir}")
    
    # Display final directory structure
    print(f"\nFinal directory structure:")
    for root, _, files in os.walk(target_dir):
        level = root.replace(str(target_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            print(f"{subindent}{file} ({file_size:,} bytes)")
    
    return True

def cleanup_orchestrator_db():
    """Delete the orchestrator database file"""
    db_path = Path("/Users/boris/projects/crunch/models-orchestrator/model_orchestrator/data/orchestrator.db")
    
    print(f"\n=== Orchestrator DB Cleanup ===")
    print(f"Checking for database file: {db_path}")
    
    try:
        if db_path.exists():
            db_path.unlink()
            print(f"✓ Deleted orchestrator database: {db_path}")
        else:
            print(f"✓ Database file not found (already clean): {db_path}")
    except Exception as e:
        print(f"⚠️  Error deleting database file: {e}")

def main():
    """Main function"""
    try:
        # First, clean up Docker resources
        cleanup_docker()
        
        # Clean up orchestrator database
        cleanup_orchestrator_db()
        
        # Then sync models
        success = sync_models()
        if success:
            print("\n✓ Models sync, Docker cleanup, and DB cleanup completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Models sync failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during sync: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()