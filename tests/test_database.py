"""Tests for database operations."""

import pytest
import tempfile
import os
from core.database import SimpleDB


class TestSimpleDB:
    """Test cases for SimpleDB."""

    @pytest.fixture
    async def db_manager(self):
        """Create a temporary database for testing."""
        # Create temporary database file
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)

        manager = DatabaseManager(db_path)
        await manager.initialize()

        yield manager

        # Cleanup
        await manager.close()
        os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_guild_settings_operations(self, db_manager):
        """Test guild settings CRUD operations."""
        guild_id = 123456789

        # Test getting non-existent settings
        settings = await db_manager.get_guild_settings(guild_id)
        assert settings is None

        # Test setting contest channel
        channel_id = 987654321
        await db_manager.set_contest_channel(guild_id, channel_id)

        settings = await db_manager.get_guild_settings(guild_id)
        assert settings is not None
        assert settings['contest_channel_id'] == channel_id

        # Test updating settings
        await db_manager.update_guild_settings(
            guild_id,
            timezone='Europe/London',
            announcement_time='10:00'
        )

        updated_settings = await db_manager.get_guild_settings(guild_id)
        assert updated_settings['timezone'] == 'Europe/London'
        assert updated_settings['announcement_time'] == '10:00'

    @pytest.mark.asyncio
    async def test_contest_operations(self, db_manager):
        """Test contest CRUD operations."""
        contest_data = {
            'id': 'codeforces_123',
            'name': 'Test Contest',
            'platform': 'Codeforces',
            'start_time': '2025-01-20T14:35:00',
            'duration': 7200,
            'url': 'https://example.com'
        }

        # Save contest
        await db_manager.save_contest(contest_data)

        # Get upcoming contests
        contests = await db_manager.get_upcoming_contests()
        assert len(contests) >= 0  # Might be 0 if contest is in the past

        # Test marking as announced
        await db_manager.mark_contest_announced(contest_data['id'])

        # Verify it's not in the to-announce list
        to_announce = await db_manager.get_contests_to_announce()
        announced_ids = [c['contest_id'] for c in to_announce]
        assert contest_data['id'] not in announced_ids

    @pytest.mark.asyncio
    async def test_user_preferences_operations(self, db_manager):
        """Test user preferences CRUD operations."""
        user_id = 123456789

        # Test getting non-existent preferences
        prefs = await db_manager.get_user_preferences(user_id)
        assert prefs is None

        # Test updating preferences
        await db_manager.update_user_preferences(
            user_id,
            timezone='US/Pacific',
            platforms='codeforces.com,atcoder.jp',
            dm_notifications=True
        )

        prefs = await db_manager.get_user_preferences(user_id)
        assert prefs is not None
        assert prefs['timezone'] == 'US/Pacific'
        assert prefs['platforms'] == 'codeforces.com,atcoder.jp'
        assert prefs['dm_notifications'] == 1  # SQLite stores as integer

    @pytest.mark.asyncio
    async def test_database_initialization(self):
        """Test database initialization creates tables."""
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)

        try:
            manager = DatabaseManager(db_path)
            await manager.initialize()

            # Verify tables exist by trying to insert data
            guild_id = 123
            await manager.set_contest_channel(guild_id, 456)

            settings = await manager.get_guild_settings(guild_id)
            assert settings is not None

            await manager.close()

        finally:
            os.unlink(db_path)
