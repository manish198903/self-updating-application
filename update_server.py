#!/usr/bin/env python3
"""
Update server for the self-updating application

This server provides version information and serves update files
"""

import argparse
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from werkzeug.exceptions import NotFound, InternalServerError

# Configuration constants
HOST = os.environ.get("HOST", "localhost")
PORT = int(os.environ.get("PORT", "8000"))
UPDATES_DIR = Path(__file__).parent / "updates"
LATEST_MANIFEST_FILE = UPDATES_DIR / "latest_manifest.json"

# TODO: Add authentication before production deployment
# Consider implementing: API keys, JWT tokens, rate limiting, IP whitelisting

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_latest_manifest() -> Optional[Dict[str, Any]]:
    """Read the latest manifest file created by create_update.py"""
    try:
        if LATEST_MANIFEST_FILE.exists():
            with open(LATEST_MANIFEST_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error reading manifest file: {e}")
    return None


def get_latest_update_file() -> Optional[Path]:
    """Get the path to the latest update file based on manifest"""
    manifest = read_latest_manifest()
    if manifest and "filename" in manifest:
        update_file = UPDATES_DIR / manifest["filename"]
        if update_file.exists():
            return update_file
    
    # Fallback to latest.zip if manifest is unavailable
    latest_zip = UPDATES_DIR / "latest.zip"
    if latest_zip.exists():
        return latest_zip
        
    return None


@app.route('/api/version')
def get_version():
    """Get current version information from manifest file"""
    try:
        manifest = read_latest_manifest()
        
        if not manifest:
            logger.error("No manifest file found - run create_update.py first")
            raise NotFound("Version information not available")
        
        logger.info(f"Served version info: {manifest['version']}")
        return jsonify(manifest)
        
    except Exception as e:
        logger.error(f"Error serving version info: {e}")
        raise InternalServerError("Error getting version info")


@app.route('/api/download')
def download_update():
    """Handle update file download requests"""
    try:
        update_file = get_latest_update_file()
        
        if not update_file or not update_file.exists():
            logger.warning(f"Update file not found for download request from {request.remote_addr}")
            raise NotFound("Update file not found")
            
        logger.info(f"Serving update file: {update_file.name}")
        return send_file(update_file)
        
    except Exception as e:
        logger.error(f"Error serving update file: {e}")
        raise InternalServerError("Error serving update file")


@app.route('/health')
def health_check():
    """Handle health check requests"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


def main():
    """Server entry point"""
    
    parser = argparse.ArgumentParser(description="Update Server for NameTag Application")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    
    args = parser.parse_args()
    
    # Override defaults with command line args
    host = args.host
    port = args.port
    
    # Check if manifest file exists
    manifest = read_latest_manifest()
    if manifest:
        logger.info(f"Found manifest for version {manifest['version']}")
    else:
        logger.warning("No manifest file found - run 'python create_update.py' first")
    
    logger.info(f"Starting NameTag Update Server")
    logger.info(f"Server: http://{host}:{port}")
    logger.info(f"Updates directory: {UPDATES_DIR}")
    
    # Start Flask server
    app.run(host=host, port=port)

if __name__ == "__main__":
    main()