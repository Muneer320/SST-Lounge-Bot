"""
GitHub auto-update functionality for SST Lounge Bot.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import asyncio
import json
import aiohttp
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger('SSTLounge.Updater')

class GitUpdater:
    """Handles checking for updates and updating the bot from GitHub."""
    
    def __init__(self, bot, check_interval=300):
        """
        Initialize the updater.
        
        Args:
            bot: The bot instance for sending notifications
            check_interval (int): How often to check for updates in seconds. Default is 5 minutes.
        """
        self.bot = bot
        self.check_interval = check_interval
        
        # Get repository URL and branch from environment variables
        self.repo_url = os.getenv('GITHUB_REPO_URL', 'https://github.com/Muneer320/SST-Lounge-Bot')
        self.branch = os.getenv('GITHUB_REPO_BRANCH', '')
        
        # If branch is empty, use default branch (usually main or master)
        self.branch_args = []
        if self.branch:
            self.branch_args = [self.branch]
        
        # Flag to control update task
        self.running = False
        
        # Parse repository info
        repo_parts = self.repo_url.split('/')
        if 'github.com' in self.repo_url and len(repo_parts) >= 5:
            self.repo_owner = repo_parts[-2]
            self.repo_name = repo_parts[-1]
        else:
            self.repo_owner = None
            self.repo_name = None
        
        # Version information
        self.version_file = Path("version.json")
        self.current_version = self._load_current_version()
        self.remote_version = None
        
        logger.info(f"GitUpdater initialized with repo: {self.repo_url}, branch: {self.branch or 'default'}")
    
    def _load_current_version(self) -> Dict[str, Any]:
        """Load the current version information from version.json."""
        try:
            if self.version_file.exists():
                with open(self.version_file, "r") as f:
                    return json.load(f)
            else:
                logger.warning("version.json not found, using default version info")
                return {
                    "version": "1.0.0",
                    "date": "2024-01-01",
                    "name": "SST Lounge Bot",
                    "branch": "main"
                }
        except Exception as e:
            logger.error(f"Error loading version info: {e}")
            return {
                "version": "1.0.0",
                "date": "2024-01-01",
                "name": "SST Lounge Bot",
                "branch": "main"
            }
    
    async def start_update_checker(self):
        """Start periodic update checking."""
        self.running = True
        
        # Initial check
        try:
            update_available, version_info = await self.check_for_updates()
            if update_available and version_info is not None:
                await self.notify_update_available(version_info)
        except Exception as e:
            logger.error(f"Error in initial update check: {e}")
        
        # Periodic checks
        while self.running:
            await asyncio.sleep(self.check_interval)
            try:
                update_available, version_info = await self.check_for_updates()
                if update_available and version_info is not None:
                    await self.notify_update_available(version_info)
            except Exception as e:
                logger.error(f"Error checking for updates: {e}")
    
    async def notify_update_available(self, version_info: Dict[str, Any]):
        """
        Notify admins about available updates.
        
        Args:
            version_info: Information about the new version
        """
        try:
            # Check if we have bot admins
            if not hasattr(self.bot, "db"):
                return
                
            # Get list of admin users
            admin_users = await self.bot.db.get_bot_admins()
            
            # Build notification message
            message = (
                f"🔄 **Update Available!** 🔄\n"
                f"Current version: {self.current_version.get('version', 'unknown')}\n"
                f"New version: {version_info.get('version', 'unknown')}\n"
                f"Released: {version_info.get('date', 'unknown')}\n"
                f"Description: {version_info.get('description', 'No description provided')}\n\n"
                f"Use `/update` to update the bot."
            )
            
            # Send DM to each admin user
            for admin in admin_users:
                try:
                    # Get the user object
                    user = self.bot.get_user(admin["user_id"])
                    if not user:
                        # Try to fetch the user if not in cache
                        try:
                            user = await self.bot.fetch_user(admin["user_id"])
                        except Exception:
                            logger.error(f"Could not fetch user {admin['user_id']}")
                            continue
                    
                    # Send the DM
                    await user.send(message)
                    logger.info(f"Sent update notification to admin {user.name} ({user.id})")
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin['user_id']}: {e}")
                    
            logger.info("Sent update notifications to admins")
        except Exception as e:
            logger.error(f"Error notifying admins about update: {e}")
    
    async def check_for_updates(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if updates are available.
        
        Returns:
            Tuple[bool, Optional[Dict]]: (update_available, version_info)
                - update_available: True if updates are available
                - version_info: Remote version info if available, None otherwise
        """
        try:
            # First check by comparing version.json (preferred method)
            if await self._check_version_file():
                return True, self.remote_version
            
            # If version check didn't find updates, fall back to commit hash comparison
            # Fetch latest changes without merging
            fetch_process = await asyncio.create_subprocess_exec(
                'git', 'fetch', 'origin', *self.branch_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await fetch_process.communicate()
            
            if fetch_process.returncode != 0:
                logger.error("Failed to fetch from remote")
                return False, None
            
            # Get current commit hash
            current_commit_process = await asyncio.create_subprocess_exec(
                'git', 'rev-parse', 'HEAD',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            current_out, _ = await current_commit_process.communicate()
            current_commit = current_out.decode().strip()
            
            # Get remote commit hash
            remote_branch = f"origin/{self.branch}" if self.branch else "origin/HEAD"
            remote_commit_process = await asyncio.create_subprocess_exec(
                'git', 'rev-parse', remote_branch,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            remote_out, _ = await remote_commit_process.communicate()
            remote_commit = remote_out.decode().strip()
            
            if current_commit != remote_commit:
                logger.info(f"Updates available via commit comparison: {current_commit[:7]} → {remote_commit[:7]}")
                # Use current version info as remote since we don't have specific version info
                self.remote_version = self.current_version.copy()
                self.remote_version["description"] = "New commits available"
                return True, self.remote_version
            else:
                logger.debug("No updates available")
                return False, None
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return False, None
    
    async def _check_version_file(self) -> bool:
        """
        Check for updates by comparing version.json with the remote version.
        
        Returns:
            bool: True if update is available, False otherwise
        """
        try:
            # If we can't determine repo info, skip this check
            if not self.repo_owner or not self.repo_name:
                return False
            
            # Construct the raw URL to version.json
            branch = self.branch or "main"  # Default to main if not specified
            version_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{branch}/version.json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(version_url) as response:
                    if response.status == 200:
                        self.remote_version = await response.json()
                        
                        # Compare versions
                        current_version = self.current_version.get("version", "0.0.0")
                        remote_version = self.remote_version.get("version", "0.0.0")
                        
                        # Convert versions to comparable tuples
                        current_parts = [int(x) for x in current_version.split('.')]
                        remote_parts = [int(x) for x in remote_version.split('.')]
                        
                        # Pad with zeros if needed
                        while len(current_parts) < 3:
                            current_parts.append(0)
                        while len(remote_parts) < 3:
                            remote_parts.append(0)
                        
                        # Compare versions
                        if remote_parts > current_parts:
                            logger.info(f"Update available: {current_version} → {remote_version}")
                            return True
                        else:
                            logger.debug(f"No update available: Current {current_version}, Remote {remote_version}")
                            return False
                    else:
                        logger.warning(f"Failed to fetch remote version info: HTTP {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error checking version file: {e}")
            return False
    
    async def update(self, interaction=None) -> bool:
        """
        Pull the latest changes and restart the bot.
        
        Args:
            interaction: Optional discord interaction for progress updates
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Send initial update message if interaction is provided
            if interaction:
                # Don't send a response here - the button already responded
                # Just use followup messages from here on
                await interaction.followup.send("🔄 Pulling latest changes from GitHub...", ephemeral=True)
                
            # Pull changes
            pull_process = await asyncio.create_subprocess_exec(
                'git', 'pull', 'origin', *self.branch_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await pull_process.communicate()
            
            if pull_process.returncode != 0:
                error_msg = f"Failed to pull changes: {stderr.decode()}"
                logger.error(error_msg)
                if interaction:
                    await interaction.followup.send(f"❌ {error_msg}", ephemeral=True)
                return False
            
            pull_output = stdout.decode()
            logger.info(f"Changes pulled successfully: {pull_output}")
            
            # Update version information
            try:
                self.current_version = self._load_current_version()
            except Exception as e:
                logger.error(f"Failed to reload version info: {e}")
            
            # Notify about successful pull
            if interaction:
                await interaction.followup.send(
                    f"✅ Changes pulled successfully!\n```\n{pull_output[:1500]}\n```\n🔄 Restarting bot...",
                    ephemeral=True
                )
            
            # Restart the bot
            logger.info("Restarting bot...")
            
            # Get the path of the current script
            script_path = Path(sys.argv[0])
            
            # Build the restart command
            restart_command = [sys.executable] + sys.argv
            
            # Start the new process
            subprocess.Popen(restart_command)
            
            # Exit the current process
            sys.exit(0)
            return True
            
        except Exception as e:
            error_msg = f"Error during update: {e}"
            logger.error(error_msg)
            if interaction:
                try:
                    await interaction.followup.send(f"❌ {error_msg}", ephemeral=True)
                except Exception as follow_error:
                    logger.error(f"Failed to send error message: {follow_error}")
            return False

    async def update_and_restart(self):
        """Pull the latest changes and restart the bot (backward compatibility)."""
        await self.update()

    def stop(self):
        """Stop the update checker."""
        self.running = False
        logger.info("Update checker stopped") 