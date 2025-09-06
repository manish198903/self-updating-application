"""
Configuration module for the self-updating application.
"""

import os
from pathlib import Path


class Config:
    """Application configuration settings"""
    
    # Application version - this should be updated with each release
    VERSION = "1.0.16"
    
    # Update server configuration
    UPDATE_SERVER_URL = os.environ.get("UPDATE_SERVER_URL", "http://localhost:8000")
    UPDATE_CHECK_ENDPOINT = "/api/version"
    UPDATE_DOWNLOAD_ENDPOINT = "/api/download"
    
    
    # Application directories
    APP_NAME = "nametag"
    HOME_DIR = Path.home() / f'.{APP_NAME}'
    BACKUP_DIR = HOME_DIR / 'backups'
    TEMP_DIR = HOME_DIR / 'temp'
    
    # Update settings
    MAX_BACKUP_COUNT = 5  # Keep last 5 versions as backups
    UPDATE_TIMEOUT = 10   # Shorter timeout for HTTP requests in seconds
    VERIFY_CHECKSUMS = True  # Whether to verify file checksums
    
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.HOME_DIR, cls.BACKUP_DIR, cls.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
    @classmethod
    def get_current_executable(cls):
        """Get the path to the current executable"""
        import sys
        return Path(sys.argv[0]).resolve()
        
    @classmethod
    def get_backup_path(cls):
        """Get the backup path base name for the current version"""
        return cls.BACKUP_DIR / f"{cls.APP_NAME}_v{cls.VERSION}"
