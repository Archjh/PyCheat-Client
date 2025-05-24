import os
import shutil
import sys
from pathlib import Path

def install_client(minecraft_dir):
    """
    Install the ArchLibman client version to the specified Minecraft directory
    """
    try:
        # Paths
        source_dir = Path(__file__).parent / "ArchLibman"
        target_dir = Path(minecraft_dir) / "versions" / "ArchLibman"
        
        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all files from source to target
        for item in source_dir.glob('*'):
            if item.is_dir():
                shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target_dir / item.name)
        
        return True, "Client installed successfully!"
    except Exception as e:
        return False, f"Installation failed: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python install_client.py <minecraft_directory>")
        sys.exit(1)
    
    success, message = install_client(sys.argv[1])
    print(message)
    sys.exit(0 if success else 1)
