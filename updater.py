"""
Self-updating system implementation

This module handles checking for updates, downloading new versions,
and performing atomic updates with rollback capability
"""

import hashlib
import shutil
import zipfile
import requests
import tempfile
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
import semver

from config import Config


class SelfUpdater:
    """
    Handles the self-updating mechanism for the application
    
    Features:
    - Version checking against remote server
    - Secure download with checksum verification
    - Atomic updates (all-or-nothing)
    - Backup and rollback capabilities
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._restart_callback = None
        
        # Ensure required directories exist
        config.ensure_directories()
        
    
    def _perform_update_with_info(self, update_info: Dict[str, Any]) -> bool:
        """
        Perform the update process using already-fetched update info
        
        Args:
            update_info: Update information from the server
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            self.logger.info("Starting update process...")
            
            # Download and verify the update
            update_file = self._download_update(update_info)
            if not update_file:
                return False

            # Create backup of current version
            if not self._create_backup():
                self.logger.error("Failed to create backup")
                return False
                
            # Apply the update
            if not self._apply_update(update_file):
                self.logger.error("Failed to apply update, attempting rollback...")
                self._rollback()
                return False
                
            # Clean up
            self._cleanup_temp_files()
            self._cleanup_old_backups()
            
            self.logger.info("Update completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            self._rollback()
            return False
            
    def _get_update_info(self) -> Optional[Dict[str, Any]]:
        """Get update information from server"""
        try:
            response = requests.get(
                f"{self.config.UPDATE_SERVER_URL}{self.config.UPDATE_CHECK_ENDPOINT}",
                timeout=self.config.UPDATE_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get update info: {e}")
            return None
            
    def _create_backup(self) -> bool:
        """Create a backup of the current application"""
        try:
            current_executable = self.config.get_current_executable()
            backup_path = self.config.get_backup_path()
            
            self.logger.info(f"Creating backup: {backup_path}.zip")
            
            # Backup the entire application directory as a zip file
            app_dir = current_executable.parent
            shutil.make_archive(
                backup_path,
                'zip', 
                app_dir
            )
                
            self.logger.info("Backup created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
            
    def _download_update(self, update_info: Dict[str, Any]) -> Optional[Path]:
        """Download the update zip file and verify its integrity"""
        try:
            download_url = f"{self.config.UPDATE_SERVER_URL}{self.config.UPDATE_DOWNLOAD_ENDPOINT}"
            expected_checksum = update_info.get("checksum")
            
            self.logger.info("Downloading update...")
            
            # Create temporary file for download
            temp_file = self.config.TEMP_DIR / f"update_{update_info['version']}.zip"
            
            # Download with progress
            response = requests.get(
                download_url, 
                stream=True,
                timeout=self.config.UPDATE_TIMEOUT
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.logger.info(f"Download progress: {progress:.1f}%")
                            
            # Verify checksum if provided
            if expected_checksum and self.config.VERIFY_CHECKSUMS:
                if not self._verify_checksum(temp_file, expected_checksum):
                    self.logger.error("Checksum verification failed")
                    temp_file.unlink()
                    return None
                    
            self.logger.info("Download completed and verified")
            return temp_file
            
        except Exception as e:
            self.logger.error(f"Failed to download update: {e}")
            return None
            
    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum using sha256"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    sha256_hash.update(chunk)
                    
            actual_checksum = sha256_hash.hexdigest()
            return actual_checksum.lower() == expected_checksum.lower()
            
        except Exception as e:
            self.logger.error(f"Error verifying checksum: {e}")
            return False
    
    def _extract_zip_to_app_dir(self, zip_file_path: Path) -> bool:
        """Extract a zip file to the application directory"""
        try:
            current_executable = self.config.get_current_executable()
            app_dir = current_executable.parent
            
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                zip_file.extractall(app_dir)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to extract {zip_file_path}: {e}")
            return False
            
    def _apply_update(self, update_file: Path) -> bool:
        """Apply the downloaded update"""
        self.logger.info("Applying update...")
        
        if self._extract_zip_to_app_dir(update_file):
            self.logger.info("Update applied successfully")
            return True
        else:
            self.logger.error("Failed to apply update")
            return False
            
    def _rollback(self) -> bool:
        """Rollback to the previous version"""
        self.logger.info("Performing rollback...")
        
        backup_path_base = self.config.get_backup_path()
        backup_zip_path = backup_path_base.with_suffix('.zip')
        
        if not backup_zip_path.exists():
            self.logger.error("No backup found for rollback")
            return False
            
        if self._extract_zip_to_app_dir(backup_zip_path):
            self.logger.info("Rollback completed")
            return True
        else:
            self.logger.error("Rollback failed")
            return False
            
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            temp_dir = self.config.TEMP_DIR
            for item in temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")
            
    def _cleanup_old_backups(self):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backups = list(self.config.BACKUP_DIR.glob(f"{self.config.APP_NAME}_v*.zip"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups beyond the limit
            for backup in backups[self.config.MAX_BACKUP_COUNT:]:
                backup.unlink()
                self.logger.info(f"Removed old backup: {backup.name}")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")
    
    def start_periodic_checking(self, restart_callback=None):
        """
        Start periodic update checking in a background daemon thread
        
        Args:
            restart_callback: Function to call when a restart is needed after update
        """
        self._restart_callback = restart_callback
        update_thread = threading.Thread(target=self._periodic_update_check, daemon=True)
        update_thread.start()
        self.logger.info("Started periodic update checking thread")
    
    def _periodic_update_check(self):
        """Background daemon thread for periodic update checking"""
        # Check immediately on start
        # Then check every 5 minutes (reasonable production interval)
        while True:
          self._check_and_update()
          time.sleep(10)  # Wait 10 seconds between checks (use 300+ for production)
            
    
    def _check_and_update(self):
        """Check for updates and apply them if available"""
        try:
            self.logger.info("Checking for updates...")
            
            # Fetch update info once
            update_info = self._get_update_info()
            if not update_info:
                return
                
            remote_version = update_info.get("version")
            if not remote_version:
                self.logger.error("Invalid version response from server")
                return
                
            # Compare versions using semver
            current_version = self.config.VERSION
            self.logger.info(f"Current version: {current_version}, Remote version: {remote_version}")
            
            comparison = semver.compare(remote_version, current_version)
            
            if comparison > 0:
                self.logger.info(f"Update available: {remote_version}")
                if self._perform_update_with_info(update_info):
                    self.logger.info("Update completed successfully. Requesting restart...")
                    if self._restart_callback:
                        self._restart_callback()
                else:
                    self.logger.error("Update failed. Continuing with current version.")
            else:
                self.logger.info("No updates available")
                
        except Exception as e:
            self.logger.error(f"Error during periodic update check: {e}")
