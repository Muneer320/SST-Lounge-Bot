"""
SST Lounge Bot - Core Bot Class
Simple and focused Discord bot for SST Batch '29.
"""

import discord
from discord.ext import commands
import logging
import os
from core.database import SimpleDB
from core.updater import GitUpdater


class SSTLoungeBot(commands.Bot):
    """SST Lounge Discord Bot."""

    def __init__(self):
        # Bot setup with only slash commands
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # Required for member join events and fetching member list

        super().__init__(
            command_prefix='!',
            intents=intents,
            case_insensitive=True
        )

        # Initialize database
        self.db = SimpleDB()

        # Initialize git updater
        update_interval = int(os.getenv('UPDATE_CHECK_INTERVAL', '300'))
        self.updater = GitUpdater(self, check_interval=update_interval)

        # Ensure logs directory exists
        from pathlib import Path
        Path("logs").mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/sst_lounge.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SSTLounge')

    async def setup_hook(self):
        """Called when the bot is starting up."""
        # Initialize database
        await self.db.initialize()

        # Load all feature modules
        await self.load_features()

        self.logger.info("Bot setup completed")

        # Start update checker if enabled
        if os.getenv('ENABLE_AUTO_UPDATES', 'true').lower() == 'true':
            self.logger.info("Starting auto-update checker")
            self.loop.create_task(self.updater.start_update_checker())
        else:
            self.logger.info("Auto-updates disabled")

    async def load_features(self):
        """Load all feature modules."""
        features = [
            'features.contests.contests',
            'features.utilities.utilities',
            'features.admin.admin',
            'features.roles.roles'
        ]

        for feature in features:
            try:
                await self.load_extension(feature)
                self.logger.info(f"Loaded feature: {feature}")
            except Exception as e:
                self.logger.error(f"Failed to load {feature}: {e}")

    async def on_ready(self):
        """Called when bot is ready."""
        self.logger.info(f"Bot {self.user} is online!")
        self.logger.info(f"Serving {len(self.guilds)} guilds")

        # Sync slash commands on startup
        try:
            synced = await self.tree.sync()
            self.logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            self.logger.error(f"Failed to sync commands: {e}")

        # Set bot activity
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="SST Batch '29 | /help"
        )
        await self.change_presence(activity=activity)

    async def on_guild_join(self, guild):
        """Called when bot joins a new guild."""
        self.logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")

    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild."""
        self.logger.info(f"Left guild: {guild.name} (ID: {guild.id})")

    async def close(self):
        """Called when bot is shutting down."""
        # Stop update checker
        if hasattr(self, 'updater'):
            self.updater.stop()

        await self.db.close()
        await super().close()
        self.logger.info("Bot shutdown completed")
