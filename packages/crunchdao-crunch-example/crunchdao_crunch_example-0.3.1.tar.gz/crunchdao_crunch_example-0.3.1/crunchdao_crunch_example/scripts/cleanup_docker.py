#!/usr/bin/env python3
"""
Standalone Docker cleanup script for crunchdao/model-runner images and containers
"""

import subprocess
import sys

def cleanup_docker():
    """Stop and remove crunchdao/model-runner containers and images"""
    print("=== Docker Cleanup for crunchdao/model-runner ===")
    
    try:
        # Check if Docker is available
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker not available")
            return False
        
        docker_version = result.stdout.strip()
        print(f"✓ Docker found: {docker_version}")
        
        # Find and stop all containers using crunchdao/model-runner images
        print("\n🔍 Looking for containers using crunchdao/model-runner images...")
        
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
                        print(f"  📦 {container} (using image {image_id[:12]})")
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
                        print(f"  📦 {container} (using crunchdao/model-runner)")
                        all_container_ids.append(container_id)
        except subprocess.CalledProcessError:
            pass
        
        if all_container_ids:
            print(f"\n📦 Found {len(all_container_ids)} total containers to remove")
            
            # Stop containers
            print(f"⏹️  Stopping containers...")
            try:
                subprocess.run(['docker', 'stop'] + all_container_ids, check=True)
                print(f"✓ Stopped {len(all_container_ids)} containers")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Some containers may already be stopped: {e}")
            
            # Remove containers
            print(f"🗑️  Removing containers...")
            for container_id in all_container_ids:
                try:
                    result = subprocess.run(['docker', 'rm', '-f', container_id], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"  ✓ Removed container {container_id[:12]}")
                    else:
                        # Check if container is already gone
                        check_result = subprocess.run(['docker', 'ps', '-a', '-q', '--filter', f'id={container_id}'], 
                                                    capture_output=True, text=True)
                        if not check_result.stdout.strip():
                            print(f"  ✓ Container {container_id[:12]} already removed")
                        else:
                            print(f"  ⚠️  Could not remove container {container_id[:12]}: {result.stderr.strip()}")
                except subprocess.CalledProcessError as e:
                    print(f"  ⚠️  Error removing container {container_id[:12]}: {e}")
            
            print(f"✓ Container removal process completed")
        else:
            print("✓ No containers found using crunchdao/model-runner images")
        
        # Remove crunchdao/model-runner images
        print("\n🔍 Looking for crunchdao/model-runner images...")
        try:
            # Get image information
            result = subprocess.run([
                'docker', 'images', 'crunchdao/model-runner', '--format', '{{.ID}} {{.Tag}} {{.Size}}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                images = result.stdout.strip().split('\n')
                print(f"🖼️  Found {len(images)} images:")
                for image in images:
                    print(f"  - {image}")
                
                # Extract just the IDs
                image_ids = [line.split()[0] for line in images]
                
                # Force remove images
                print(f"\n🗑️  Removing {len(image_ids)} images...")
                subprocess.run(['docker', 'rmi', '-f'] + image_ids, check=True)
                print(f"✓ Removed {len(image_ids)} images")
            else:
                print("✓ No images found for crunchdao/model-runner")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error removing images: {e}")
            return False
        
        # Clean up dangling images and containers
        print("\n🧹 Cleaning up dangling Docker resources...")
        try:
            result = subprocess.run(['docker', 'system', 'prune', '-f'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print(f"✓ {result.stdout.strip()}")
            else:
                print("✓ No dangling resources to clean")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning during system cleanup: {e}")
        
        print("\n✅ Docker cleanup completed successfully!")
        return True
            
    except Exception as e:
        print(f"❌ Docker cleanup failed: {e}")
        return False

def main():
    """Main function"""
    try:
        success = cleanup_docker()
        if success:
            sys.exit(0)
        else:
            print("\n❌ Docker cleanup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()