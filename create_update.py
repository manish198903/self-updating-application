#!/usr/bin/env python3

"""Simple script to increment version and create update zip"""

import json
import zipfile
import hashlib
import semver
from datetime import datetime, timezone
from pathlib import Path
from config import Config

def main():
    print("NameTag Update Creator")
    print("=" * 24)
    
    # Get current version from config
    current_version = Config.VERSION
    print(f"Current version: {current_version}")
    
    # Increment patch version using semver
    new_version = semver.bump_patch(current_version)
    print(f"New version: {new_version}")
    
    # Update version in config.py
    print("Updating config.py...")
    config_file = Path("config.py")
    config_content = config_file.read_text()
    new_config_content = config_content.replace(
        f'VERSION = "{current_version}"',
        f'VERSION = "{new_version}"'
    )
    config_file.write_text(new_config_content)
    print("[SUCCESS] Updated version in config.py")
    
    # Create updates directory if it doesn't exist
    updates_dir = Path("updates")
    updates_dir.mkdir(exist_ok=True)
    
    # Define files to include in the update
    files_to_include = ["program.py", "updater.py", "config.py", "requirements.txt"]
    
    # Create the update zip
    zip_file = updates_dir / f"{Config.APP_NAME}_v{new_version}.zip"
    print(f"Creating update package: {zip_file}")
    
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_name in files_to_include:
            zf.write(file_name)
    
    print("[SUCCESS] Created update package")
    
    # Calculate SHA256 checksum
    checksum = hashlib.sha256()
    with open(zip_file, 'rb') as f:
        while chunk := f.read(4096):
            checksum.update(chunk)
    
    file_size = zip_file.stat().st_size
    checksum_hex = checksum.hexdigest()
    
    # Create version manifest
    manifest_file = updates_dir / f"manifest_v{new_version}.json"
    manifest = {
        "version": new_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "filename": f"{Config.APP_NAME}_v{new_version}.zip",
        "checksum": checksum_hex,
        "size": file_size,
        "changelog": f"Updated to version {new_version}"
    }
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f)
    
    # Create/update latest manifest symlink
    latest_manifest = updates_dir / "latest_manifest.json"
    if latest_manifest.exists() or latest_manifest.is_symlink():
        latest_manifest.unlink()
    latest_manifest.symlink_to(f"manifest_v{new_version}.json")
    
    # Create/update latest symlink
    latest_zip = updates_dir / "latest.zip"
    if latest_zip.exists() or latest_zip.is_symlink():
        latest_zip.unlink()
    latest_zip.symlink_to(f"{Config.APP_NAME}_v{new_version}.zip")
    
    print()
    print("Update package created successfully!")
    print(f"  File: {zip_file}")
    print(f"  Size: {file_size} bytes")
    print(f"  Checksum: {checksum_hex}")
    print(f"  Manifest: {manifest_file}")
    print()
    print("To test the update:")
    print("  1. Start update server: python update_server.py")
    print("  2. Run application: python program.py")
    
    return 0

if __name__ == "__main__":
    main()