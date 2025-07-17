"""
Enhanced Database for SST Lounge Bot
Handles guild settings, contest caching, and user preferences.
"""

import aiosqlite
import logging
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime, timedelta


class SimpleDB:
    """Enhanced database for bot settings and contest caching."""

    def __init__(self, db_path: str = "database/sst_lounge.db"):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        """Initialize database."""
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        logging.info(f"Database initialized at {self.db_path}")

    async def _create_tables(self):
        """Create necessary tables."""
        if not self.connection:
            return

        # Guild settings table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                contest_channel_id INTEGER,
                announcement_time TEXT DEFAULT '09:00',
                last_announcement DATE,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Contest cache table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS contest_cache (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration INTEGER NOT NULL,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Index for faster queries
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_contest_platform_time 
            ON contest_cache(platform, start_time)
        """)

        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_contest_start_time 
            ON contest_cache(start_time)
        """)

        # Bot admins table for custom bot-level admin privileges
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS bot_admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER,
                role_id INTEGER,
                granted_by INTEGER NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, user_id, role_id)
            )
        """)

        await self.connection.commit()

    # Guild Settings Methods
    async def set_contest_channel(self, guild_id: int, channel_id: int):
        """Set contest announcement channel for a guild."""
        if not self.connection:
            return
        await self.connection.execute("""
            INSERT OR REPLACE INTO guild_settings (guild_id, contest_channel_id) 
            VALUES (?, ?)
        """, (guild_id, channel_id))
        await self.connection.commit()

    async def get_contest_channel(self, guild_id: int) -> Optional[int]:
        """Get contest channel for a guild."""
        if not self.connection:
            return None
        cursor = await self.connection.execute("""
            SELECT contest_channel_id FROM guild_settings WHERE guild_id = ?
        """, (guild_id,))
        result = await cursor.fetchone()
        return result[0] if result else None

    async def get_all_contest_channels(self) -> Dict[int, int]:
        """Get all guild contest channels."""
        if not self.connection:
            return {}
        cursor = await self.connection.execute("""
            SELECT guild_id, contest_channel_id FROM guild_settings 
            WHERE contest_channel_id IS NOT NULL
        """)
        results = await cursor.fetchall()
        return {guild_id: channel_id for guild_id, channel_id in results}

    async def set_announcement_time(self, guild_id: int, time: str):
        """Set announcement time for a guild (format: HH:MM)."""
        if not self.connection:
            return
        await self.connection.execute("""
            INSERT OR REPLACE INTO guild_settings 
            (guild_id, contest_channel_id, announcement_time) 
            VALUES (?, COALESCE((SELECT contest_channel_id FROM guild_settings WHERE guild_id = ?), NULL), ?)
        """, (guild_id, guild_id, time))
        await self.connection.commit()

    async def get_announcement_time(self, guild_id: int) -> str:
        """Get announcement time for a guild."""
        if not self.connection:
            return "09:00"
        cursor = await self.connection.execute("""
            SELECT announcement_time FROM guild_settings WHERE guild_id = ?
        """, (guild_id,))
        result = await cursor.fetchone()
        return result[0] if result else "09:00"

    async def mark_announcement_sent(self, guild_id: int):
        """Mark that announcement was sent today for a guild."""
        if not self.connection:
            return
        today = datetime.now().date().isoformat()
        await self.connection.execute("""
            UPDATE guild_settings SET last_announcement = ? WHERE guild_id = ?
        """, (today, guild_id))
        await self.connection.commit()

    async def should_send_announcement(self, guild_id: int) -> bool:
        """Check if announcement should be sent for a guild today."""
        if not self.connection:
            return False
        today = datetime.now().date().isoformat()
        cursor = await self.connection.execute("""
            SELECT last_announcement FROM guild_settings WHERE guild_id = ?
        """, (guild_id,))
        result = await cursor.fetchone()
        last_announcement = result[0] if result else None
        return last_announcement != today

    # Contest Cache Methods
    async def cache_contests(self, contests: List[Dict]):
        """Cache contests in database."""
        if not self.connection:
            return
        # Clear old cache
        await self.connection.execute("DELETE FROM contest_cache")

        for contest in contests:
            await self.connection.execute("""
                INSERT OR REPLACE INTO contest_cache 
                (id, name, platform, start_time, end_time, duration, url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                contest['id'],
                contest['name'],
                contest['platform'],
                contest['start_time'],
                contest['end_time'],
                contest['duration'],
                contest['url']
            ))

        await self.connection.commit()
        logging.info(f"Cached {len(contests)} contests")

    async def get_cached_contests(self,
                                  platform: Optional[str] = None,
                                  limit: Optional[int] = None,
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> List[Dict]:
        """Get cached contests with optional filters."""
        if not self.connection:
            return []
        query = "SELECT * FROM contest_cache WHERE 1=1"
        params = []

        if platform:
            # Convert platform key to display name for database lookup
            platform_name = self._get_platform_name_from_key(platform)
            query += " AND platform = ?"
            params.append(platform_name)

        if start_date:
            query += " AND start_time >= ?"
            params.append(start_date)

        if end_date:
            query += " AND start_time <= ?"
            params.append(end_date)

        query += " ORDER BY start_time"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor = await self.connection.execute(query, params)
        results = await cursor.fetchall()

        # Convert to list of dicts
        contests = []
        for row in results:
            # Parse the stored datetime and format it nicely
            start_dt = datetime.fromisoformat(row[3])
            formatted_start = start_dt.strftime('%B %d, %Y at %I:%M %p IST')

            contests.append({
                'id': row[0],
                'name': row[1],
                'platform': row[2],
                'start_time': formatted_start,
                'end_time': row[4],
                'duration': self._format_duration_from_seconds(row[5]),
                'duration_seconds': row[5],  # Add raw duration in seconds
                'url': row[6],
                'created_at': row[7],
                'updated_at': row[8],
                'platform_key': self._get_platform_key_from_name(row[2])
            })

        return contests

    def _get_platform_name_from_key(self, platform_key: str) -> str:
        """Get platform display name from platform key."""
        key_to_name = {
            'codeforces.com': 'Codeforces',
            'codechef.com': 'CodeChef',
            'atcoder.jp': 'AtCoder',
            'leetcode.com': 'LeetCode'
        }
        return key_to_name.get(platform_key, platform_key)

    def _format_duration_from_seconds(self, seconds: int) -> str:
        """Format duration in seconds to readable string."""
        if not seconds:
            return "Unknown"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours and minutes:
            return f"{hours}h {minutes}m"
        elif hours:
            return f"{hours}h"
        elif minutes:
            return f"{minutes}m"
        else:
            return "< 1m"

    def _get_platform_key_from_name(self, platform_name: str) -> str:
        """Get platform key from platform display name."""
        platform_map = {
            'Codeforces': 'codeforces.com',
            'CodeChef': 'codechef.com',
            'AtCoder': 'atcoder.jp',
            'LeetCode': 'leetcode.com'
        }
        return platform_map.get(platform_name, platform_name.lower())

    async def get_contests_today(self, platform: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get contests starting today."""
        today = datetime.now().date()
        start_date = today.isoformat()
        end_date = (today + timedelta(days=1)).isoformat()

        return await self.get_cached_contests(
            platform=platform,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )

    async def get_contests_tomorrow(self, platform: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get contests starting tomorrow."""
        tomorrow = datetime.now().date() + timedelta(days=1)
        start_date = tomorrow.isoformat()
        end_date = (tomorrow + timedelta(days=1)).isoformat()

        return await self.get_cached_contests(
            platform=platform,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )

    async def get_cache_age(self) -> Optional[datetime]:
        """Get the age of the contest cache."""
        if not self.connection:
            return None
        cursor = await self.connection.execute("""
            SELECT MAX(updated_at) FROM contest_cache
        """)
        result = await cursor.fetchone()
        if result and result[0]:
            return datetime.fromisoformat(result[0])
        return None

    async def is_cache_stale(self, max_age_hours: int = 6) -> bool:
        """Check if cache is stale and needs refreshing."""
        cache_age = await self.get_cache_age()
        if not cache_age:
            return True  # No cache exists

        age_delta = datetime.now() - cache_age
        return age_delta.total_seconds() > (max_age_hours * 3600)

    async def fetch_and_cache_contests(self, api, max_days: int = 30) -> int:
        """Fetch contests from API and cache them for extended period."""
        if not self.connection:
            return 0

        try:
            # Fetch contests for max_days
            contests = await api.fetch_upcoming_contests(max_days)

            if not contests:
                return 0

            # Clear old cache
            await self.connection.execute("DELETE FROM contest_cache")

            # Cache new contests with more detailed data
            cached_count = 0
            for contest in contests:
                try:
                    # Generate unique ID based on platform and contest name
                    contest_id = f"{contest['platform'].lower()}_{hash(contest['name'])}"

                    # Parse the formatted start time string back to datetime
                    start_time_str = contest['start_time']
                    # Remove " IST" and parse
                    start_time_clean = start_time_str.replace(' IST', '')

                    # Parse format like "July 17, 2025 at 08:30 AM"
                    from datetime import datetime
                    start_dt = datetime.strptime(
                        start_time_clean, '%B %d, %Y at %I:%M %p')

                    # Calculate end time using duration
                    duration_str = contest['duration']
                    duration_seconds = contest.get('duration_seconds', 0)

                    if duration_seconds == 0:
                        # Parse duration string like "2h 30m" if seconds not available
                        duration_parts = duration_str.replace(
                            'h', '').replace('m', '').split()
                        if len(duration_parts) >= 1:
                            hours = int(
                                duration_parts[0]) if duration_parts[0].isdigit() else 0
                            minutes = int(duration_parts[1]) if len(
                                duration_parts) > 1 and duration_parts[1].isdigit() else 0
                            duration_seconds = (hours * 3600) + (minutes * 60)

                    end_dt = start_dt + timedelta(seconds=duration_seconds)

                    await self.connection.execute("""
                        INSERT OR REPLACE INTO contest_cache 
                        (id, name, platform, start_time, end_time, duration, url, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        contest_id,
                        contest['name'],
                        contest['platform'],
                        start_dt.isoformat(),
                        end_dt.isoformat(),
                        duration_seconds,
                        contest.get('url', '')
                    ))
                    cached_count += 1

                except Exception as e:
                    logging.warning(
                        f"Error caching contest {contest.get('name', 'unknown')}: {e}")
                    continue

            await self.connection.commit()
            logging.info(
                f"Cached {cached_count} contests from {len(contests)} fetched")
            return cached_count

        except Exception as e:
            logging.error(f"Error caching contests: {e}")
            return 0

    # Bot Admin Methods
    async def grant_bot_admin(self, guild_id: int, user_id: Optional[int] = None, role_id: Optional[int] = None, granted_by: Optional[int] = None):
        """Grant bot admin privileges to a user or role."""
        if not self.connection:
            return False

        if not user_id and not role_id:
            return False

        try:
            await self.connection.execute("""
                INSERT OR REPLACE INTO bot_admins (guild_id, user_id, role_id, granted_by)
                VALUES (?, ?, ?, ?)
            """, (guild_id, user_id, role_id, granted_by))
            await self.connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error granting bot admin: {e}")
            return False

    async def revoke_bot_admin(self, guild_id: int, user_id: Optional[int] = None, role_id: Optional[int] = None):
        """Revoke bot admin privileges from a user or role."""
        if not self.connection:
            return False

        if not user_id and not role_id:
            return False

        try:
            if user_id:
                await self.connection.execute("""
                    DELETE FROM bot_admins WHERE guild_id = ? AND user_id = ?
                """, (guild_id, user_id))
            elif role_id:
                await self.connection.execute("""
                    DELETE FROM bot_admins WHERE guild_id = ? AND role_id = ?
                """, (guild_id, role_id))
            await self.connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error revoking bot admin: {e}")
            return False

    async def is_bot_admin(self, guild_id: int, user_id: int, user_roles: Optional[List[int]] = None) -> bool:
        """Check if a user has bot admin privileges."""
        if not self.connection:
            return False

        try:
            # Check direct user admin privileges
            cursor = await self.connection.execute("""
                SELECT 1 FROM bot_admins WHERE guild_id = ? AND user_id = ?
            """, (guild_id, user_id))
            if await cursor.fetchone():
                return True

            # Check role-based admin privileges
            if user_roles:
                placeholders = ','.join('?' * len(user_roles))
                cursor = await self.connection.execute(f"""
                    SELECT 1 FROM bot_admins 
                    WHERE guild_id = ? AND role_id IN ({placeholders})
                """, [guild_id] + user_roles)
                if await cursor.fetchone():
                    return True

            return False
        except Exception as e:
            logging.error(f"Error checking bot admin: {e}")
            return False

    async def get_bot_admins(self, guild_id: int) -> List[Dict]:
        """Get all bot admins for a guild."""
        if not self.connection:
            return []

        try:
            cursor = await self.connection.execute("""
                SELECT user_id, role_id, granted_by, granted_at 
                FROM bot_admins WHERE guild_id = ?
                ORDER BY granted_at DESC
            """, (guild_id,))

            admins = []
            async for row in cursor:
                admins.append({
                    'user_id': row[0],
                    'role_id': row[1],
                    'granted_by': row[2],
                    'granted_at': row[3]
                })
            return admins
        except Exception as e:
            logging.error(f"Error getting bot admins: {e}")
            return []

    async def close(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
