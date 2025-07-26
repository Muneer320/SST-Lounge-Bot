"""
SST Lounge Bot - Core Bot Class
Simple and focused Discord bot for SST Batch '29.
"""

import discord
from discord.ext import commands
import logging
import os
from pathlib import Path
from core.database import SimpleDB
from core.updater import GitUpdater
from utils.mention_response import MentionResponseHandler


class SSTLoungeBot(commands.Bot):
    """SST Lounge Discord Bot."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            case_insensitive=True
        )

        self.db = SimpleDB()

        update_interval = int(os.getenv('UPDATE_CHECK_INTERVAL', '300'))
        self.updater = GitUpdater(self, check_interval=update_interval)

        self.mention_handler = MentionResponseHandler(self)

        Path("logs").mkdir(exist_ok=True)

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
        await self.db.initialize()
        await self.load_features()
        self.logger.info("Bot setup completed")

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

        try:
            synced = await self.tree.sync()
            self.logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            self.logger.error(f"Failed to sync commands: {e}")

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

    async def on_message(self, message):
        """Handle bot mentions with friendly greeting and helpful buttons."""
        if message.author.bot:
            return

        if self.user in message.mentions:
            await self.mention_handler.send_mention_response(message)

        await self.process_commands(message)

    async def close(self):
        """Called when bot is shutting down."""
        if hasattr(self, 'updater'):
            self.updater.stop()

        await self.db.close()
        await super().close()
        self.logger.info("Bot shutdown completed")
