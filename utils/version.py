"""
Version utility module for loading version information from version.json
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_version_info() -> Dict[str, Any]:
    """
    Load version information from version.json
    
    Returns:
        Dict containing version info with fallback values if file not found
    """
    version_file = Path("version.json")
    
    try:
        if version_file.exists():
            with open(version_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            logger.warning("version.json not found, using default version info")
            return {
                "version": "1.0.0",
                "date": "2025-07-15",
                "name": "SST Lounge Bot",
                "description": "Discord bot for SST '29 Batch",
                "version_description": "Complete codebase cleanup and documentation updates",
                "branch": "main",
                "author": "Unofficial SST Team",
                "repository": "https://github.com/Muneer320/SST-Lounge-Bot"
            }
    except Exception as e:
        logger.error(f"Error loading version info: {e}")
        return {
            "version": "1.5.0",
            "date": "2025-07-22",
            "name": "SST Lounge Bot",
            "description": "Discord bot for SST '29 Batch",
            "version_description": "Major cleanup: Fixed interaction errors, enhanced logs export, improved error handling",
            "branch": "main",
            "author": "Unofficial SST Team",
            "repository": "https://github.com/Muneer320/SST-Lounge-Bot"
        }

def get_bot_name() -> str:
    """Get the bot name from version.json"""
    return load_version_info().get("name", "SST Lounge Bot")

def get_bot_version() -> str:
    """Get the bot version from version.json"""
    return load_version_info().get("version", "1.0.0")

def get_bot_description() -> str:
    """Get the bot description from version.json"""
    return load_version_info().get("description", "Discord bot for SST '29 Batch")

def get_repository_url() -> str:
    """Get the repository URL from version.json"""
    return load_version_info().get("repository", "https://github.com/Muneer320/SST-Lounge-Bot")
