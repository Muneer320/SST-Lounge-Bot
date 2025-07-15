"""
Simple Database for SST Lounge Bot
Lightweight database operations.
"""

import aiosqlite
import logging
from typing import Optional, Dict
from pathlib import Path


class SimpleDB:
    """Simple database for bot settings."""

    def __init__(self, db_path: str = "sst_lounge.db"):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        """Initialize database."""
        Path("logs").mkdir(exist_ok=True)
        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        logging.info("Database initialized")

    async def _create_tables(self):
        """Create necessary tables."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                contest_channel_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self.connection.commit()

    async def set_contest_channel(self, guild_id: int, channel_id: int):
        """Set contest announcement channel for a guild."""
        await self.connection.execute("""
            INSERT OR REPLACE INTO guild_settings (guild_id, contest_channel_id) 
            VALUES (?, ?)
        """, (guild_id, channel_id))
        await self.connection.commit()

    async def get_contest_channel(self, guild_id: int) -> Optional[int]:
        """Get contest channel for a guild."""
        cursor = await self.connection.execute("""
            SELECT contest_channel_id FROM guild_settings WHERE guild_id = ?
        """, (guild_id,))
        result = await cursor.fetchone()
        return result[0] if result else None

    async def get_all_contest_channels(self) -> Dict[int, int]:
        """Get all guild contest channels."""
        cursor = await self.connection.execute("""
            SELECT guild_id, contest_channel_id FROM guild_settings 
            WHERE contest_channel_id IS NOT NULL
        """)
        results = await cursor.fetchall()
        return {guild_id: channel_id for guild_id, channel_id in results}

    async def close(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
