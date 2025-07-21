"""
Contest Feature Module
Contest tracking system for SST Lounge Discord Bot.
"""

import os
import logging
import aiohttp
import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import discord
from discord.ext import commands, tasks
from discord import app_commands
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import utility functions
from features.admin.admin import is_admin
from utils.interaction_helpers import safe_response, safe_defer

# Platforms for autocomplete
PLATFORMS = ['codeforces', 'codechef', 'atcoder', 'leetcode']

# Autocomplete function for platform parameter


async def platform_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=platform.capitalize(), value=platform)
        for platform in PLATFORMS if current.lower() in platform.lower()
    ]

# Autocomplete function for channel parameter


async def channel_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    if not interaction.guild or not isinstance(interaction.user, discord.Member):
        return []

    # Get all text channels the user can see
    channels = [
        channel for channel in interaction.guild.text_channels
        if channel.permissions_for(interaction.user).view_channel
    ]

    # Filter based on current input
    filtered_channels = [
        app_commands.Choice(name=f"#{channel.name}", value=str(channel.id))
        for channel in channels if current.lower() in channel.name.lower()
    ]

    # Add current channel if no input
    if not current and interaction.channel and isinstance(interaction.channel, discord.TextChannel):
        filtered_channels.insert(0, app_commands.Choice(
            name=f"#{interaction.channel.name} (current)", value=str(interaction.channel.id)))

    return filtered_channels[:25]  # Discord has a limit of 25 choices


class ContestAPI:
    """Handles contest data fetching from clist.by API."""

    def __init__(self):
        self.base_url = "https://clist.by/api/v4/contest/"
        self.username = os.getenv('CLIST_API_USERNAME')
        self.api_key = os.getenv('CLIST_API_KEY')
        self.platforms = ['codeforces.com',
                          'codechef.com', 'atcoder.jp', 'leetcode.com']
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self):
        if self.session is None or self.session.closed:
            # Create session with authentication headers if credentials are available
            headers = {}
            if self.username and self.api_key:
                headers['Authorization'] = f'ApiKey {self.username}:{self.api_key}'
                logging.info(
                    f"Using clist.by API credentials for user: {self.username}")
            else:
                logging.warning(
                    "No clist.by API credentials found - using unauthenticated requests (limited)")

            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch_upcoming_contests(self, days: int = 3) -> List[Dict]:
        """Fetch upcoming contests from API."""
        try:
            session = await self.get_session()

            # Time range for API - start from today's 00:00 UTC to get all today's contests
            start_time = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=days)

            params = {
                'start__gte': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'start__lte': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'resource__in': ','.join(self.platforms),
                'order_by': 'start',
                'format': 'json',
                'limit': 1000  # Get more contests for caching
            }

            # Log the complete URL being used
            url_with_params = f"{self.base_url}?" + \
                "&".join([f"{k}={v}" for k, v in params.items()])
            logging.info(f"Fetching contests from: {url_with_params}")

            async with session.get(self.base_url, params=params) as response:
                logging.info(f"API Response Status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    contest_count = len(data.get('objects', []))
                    logging.info(
                        f"Successfully fetched {contest_count} contests")
                    return self._process_contests(data.get('objects', []))
                elif response.status == 401:
                    logging.error(
                        "API Error 401: Unauthorized - Invalid or missing API credentials")
                    raise Exception("API_UNAUTHORIZED")
                elif response.status == 429:
                    logging.error("API Error 429: Rate limited")
                    raise Exception("API_RATE_LIMITED")
                else:
                    error_text = await response.text()
                    logging.error(f"API Error {response.status}: {error_text}")
                    raise Exception(f"API_ERROR_{response.status}")

        except Exception as e:
            logging.error(f"Contest fetch error: {e}")
            raise e

    def _process_contests(self, raw_contests: List[Dict]) -> List[Dict]:
        """Process and format contest data."""
        processed = []
        platform_names = {
            'codeforces.com': 'Codeforces',
            'codechef.com': 'CodeChef',
            'atcoder.jp': 'AtCoder',
            'leetcode.com': 'LeetCode'
        }

        for contest in raw_contests:
            try:
                # Parse start time to IST
                start_dt = datetime.fromisoformat(
                    contest['start'].replace('Z', '+00:00'))
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=pytz.UTC)
                ist_time = start_dt.astimezone(pytz.timezone('Asia/Kolkata'))

                # Calculate end time
                duration_seconds = contest.get('duration', 0)
                end_dt = start_dt + timedelta(seconds=duration_seconds)
                ist_end_time = end_dt.astimezone(pytz.timezone('Asia/Kolkata'))

                # Format duration
                duration_str = self._format_duration(duration_seconds)

                processed.append({
                    'id': f"{contest['resource']}_{hash(contest['event'])}",
                    'name': contest['event'],
                    'platform': platform_names.get(contest['resource'], contest['resource']),
                    'start_time': ist_time.strftime('%B %d, %Y at %I:%M %p IST'),
                    'end_time': ist_end_time.strftime('%B %d, %Y at %I:%M %p IST'),
                    'duration': duration_str,
                    'duration_seconds': duration_seconds,
                    'url': contest.get('href', ''),
                    'platform_emoji': self._get_emoji(contest['resource']),
                    'platform_key': contest['resource']
                })
            except Exception as e:
                logging.warning(f"Error processing contest: {e}")
                continue

        return processed

    def _format_duration(self, seconds: int) -> str:
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

    def _get_emoji(self, platform: str) -> str:
        """Get emoji for platform."""
        emojis = {
            'codeforces.com': '🔵',
            'codechef.com': '🟤',
            'atcoder.jp': '🟠',
            'leetcode.com': '🟡'
        }
        return emojis.get(platform, '⚪')

    def _get_contest_status(self, start_time_str: str, duration_seconds: int) -> str:
        """Determine contest status based on current time."""
        try:
            # Parse the formatted start time back to datetime
            start_time_clean = start_time_str.replace(' IST', '')
            start_dt = datetime.strptime(
                start_time_clean, '%B %d, %Y at %I:%M %p')

            # Convert to IST timezone for comparison
            ist_tz = pytz.timezone('Asia/Kolkata')
            start_dt = ist_tz.localize(start_dt)
            end_dt = start_dt + timedelta(seconds=duration_seconds)

            # Get current time in IST
            now_ist = datetime.now(ist_tz)

            if now_ist < start_dt:
                return "upcoming"
            elif now_ist > end_dt:
                return "ended"
            else:
                return "running"
        except Exception as e:
            logging.warning(f"Error determining contest status: {e}")
            return "unknown"

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for contest status."""
        status_emojis = {
            'upcoming': '⏰',
            'running': '🔴',
            'ended': '✅',
            'unknown': '❓'
        }
        return status_emojis.get(status, '❓')

    async def fetch_todays_contests(self) -> List[Dict]:
        """Fetch contests from today's 00:00 hours to capture all of today's contests."""
        try:
            session = await self.get_session()

            # Get today's start time at 00:00 UTC
            today_start = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            params = {
                'start__gte': today_start.strftime('%Y-%m-%dT%H:%M:%S'),
                'start__lte': today_end.strftime('%Y-%m-%dT%H:%M:%S'),
                'resource__in': ','.join(self.platforms),
                'order_by': 'start',
                'format': 'json',
                'limit': 1000
            }

            # Log the complete URL being used
            url_with_params = f"{self.base_url}?" + \
                "&".join([f"{k}={v}" for k, v in params.items()])
            logging.info(f"Fetching today's contests from: {url_with_params}")

            async with session.get(self.base_url, params=params) as response:
                logging.info(f"API Response Status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    contest_count = len(data.get('objects', []))
                    logging.info(
                        f"Successfully fetched {contest_count} today's contests")
                    return self._process_contests(data.get('objects', []))
                elif response.status == 401:
                    logging.error(
                        "API Error 401: Unauthorized - Invalid or missing API credentials")
                    raise Exception("API_UNAUTHORIZED")
                elif response.status == 429:
                    logging.error("API Error 429: Rate limited")
                    raise Exception("API_RATE_LIMITED")
                else:
                    error_text = await response.text()
                    logging.error(f"API Error {response.status}: {error_text}")
                    raise Exception(f"API_ERROR_{response.status}")

        except Exception as e:
            logging.error(f"Today's contest fetch error: {e}")
            raise e

    def _get_platform_name_from_key(self, platform_key: str) -> str:
        """Get platform display name from platform key."""
        key_to_name = {
            'codeforces.com': 'Codeforces',
            'codechef.com': 'CodeChef',
            'atcoder.jp': 'AtCoder',
            'leetcode.com': 'LeetCode'
        }
        return key_to_name.get(platform_key, platform_key)


class ContestCommands(commands.Cog):
    """Contest-related slash commands with caching and automation."""

    def __init__(self, bot):
        self.bot = bot
        self.api = ContestAPI()
        self.platform_map = {
            'codeforces': 'codeforces.com',
            'codechef': 'codechef.com',
            'atcoder': 'atcoder.jp',
            'leetcode': 'leetcode.com'
        }

        # Start background tasks
        self.refresh_contest_cache.start()
        self.daily_announcements.start()

    async def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.refresh_contest_cache.cancel()
        self.daily_announcements.cancel()
        await self.api.close()

    @tasks.loop(hours=6)  # Refresh cache every 6 hours
    async def refresh_contest_cache(self):
        """Background task to refresh contest cache."""
        try:
            logging.info("Refreshing contest cache...")
            cached_count = await self.bot.db.fetch_and_cache_contests(self.api, max_days=30)
            logging.info(f"Cache refreshed with {cached_count} contests")
        except Exception as e:
            logging.error(f"Error refreshing contest cache: {e}")

    @refresh_contest_cache.before_loop
    async def before_refresh_contest_cache(self):
        """Wait for bot to be ready before starting cache refresh."""
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=60)  # Check every hour for announcements
    async def daily_announcements(self):
        """Background task for daily contest announcements."""
        try:
            # Get all configured contest channels
            channels = await self.bot.db.get_all_contest_channels()

            for guild_id, channel_id in channels.items():
                try:
                    # Check if announcement should be sent today
                    if not await self.bot.db.should_send_announcement(guild_id):
                        continue

                    # Get announcement time for this guild
                    announcement_time = await self.bot.db.get_announcement_time(guild_id)
                    current_time = datetime.now()
                    target_time = datetime.strptime(announcement_time, '%H:%M').time()
                    
                    # Check if current time matches announcement time (within 1 hour window)
                    current_hour_min = current_time.strftime('%H:%M')
                    if current_hour_min == announcement_time:

                        guild = self.bot.get_guild(guild_id)
                        if not guild:
                            continue

                        channel = guild.get_channel(channel_id)
                        if not channel:
                            continue

                        # Send daily contest announcement
                        await self._send_daily_announcement(channel)
                        await self.bot.db.mark_announcement_sent(guild_id)

                except Exception as e:
                    logging.error(
                        f"Error sending daily announcement for guild {guild_id}: {e}")

        except Exception as e:
            logging.error(f"Error in daily announcements task: {e}")

    @daily_announcements.before_loop
    async def before_daily_announcements(self):
        """Wait for bot to be ready before starting daily announcements."""
        await self.bot.wait_until_ready()

    async def _send_daily_announcement(self, channel):
        """Send daily contest announcement to a channel."""
        try:
            # Get today's and tomorrow's contests from cache
            today_contests = await self.bot.db.get_contests_today()
            tomorrow_contests = await self.bot.db.get_contests_tomorrow()

            embed = discord.Embed(
                title="📅 Daily Contest Update",
                description="Here are the programming contests for today and tomorrow:",
                color=0x3498db
            )

            if today_contests:
                today_text = []
                for contest in today_contests[:5]:
                    emoji = self._get_emoji(contest.get('platform_key', ''))
                    today_text.append(
                        f"{emoji} **{contest['name']}** ({contest['platform']})")

                embed.add_field(
                    name="🗓️ Today's Contests",
                    value="\n".join(today_text),
                    inline=False
                )

            if tomorrow_contests:
                tomorrow_text = []
                for contest in tomorrow_contests[:5]:
                    emoji = self._get_emoji(contest.get('platform_key', ''))
                    tomorrow_text.append(
                        f"{emoji} **{contest['name']}** ({contest['platform']})")

                embed.add_field(
                    name="🌅 Tomorrow's Contests",
                    value="\n".join(tomorrow_text),
                    inline=False
                )

            if not today_contests and not tomorrow_contests:
                embed.add_field(
                    name="😴 No Contests",
                    value="No contests scheduled for today or tomorrow.",
                    inline=False
                )

            embed.add_field(
                name="💡 Tip",
                value="Use `/contests` to see more contests, or `/contests_today` and `/contests_tomorrow` for specific days!",
                inline=False
            )

            embed.set_footer(text="All times in IST • Data from clist.by")
            await channel.send(embed=embed)

        except Exception as e:
            logging.error(f"Error sending daily announcement: {e}")

    def _get_emoji(self, platform: str) -> str:
        """Get emoji for platform."""
        emojis = {
            'codeforces.com': '🔵',
            'codechef.com': '🟤',
            'atcoder.jp': '🟠',
            'leetcode.com': '🟡'
        }
        return emojis.get(platform, '⚪')

    async def _get_contests_from_cache_or_api(self, platform: Optional[str] = None,
                                              limit: Optional[int] = None,
                                              days: int = 3) -> List[Dict]:
        """Get contests from cache if available, otherwise fetch from API."""
        try:
            # Check if cache is stale
            if await self.bot.db.is_cache_stale():
                logging.info("Cache is stale, refreshing...")
                await self.bot.db.fetch_and_cache_contests(self.api, max_days=30)

            # Get from cache with proper date range
            start_date = datetime.now().date().isoformat()
            end_date = (datetime.now().date() +
                        timedelta(days=days)).isoformat()

            # Convert platform name to key if provided
            platform_key = None
            if platform:
                platform_key = self.platform_map.get(platform.lower())
                logging.info(
                    f"Filtering by platform: {platform} -> {platform_key}")

            contests = await self.bot.db.get_cached_contests(
                platform=platform_key,
                limit=limit,
                start_date=start_date,
                end_date=end_date
            )

            logging.info(f"Retrieved {len(contests)} contests from cache")
            return contests

        except Exception as e:
            logging.warning(
                f"Error getting contests from cache, falling back to API: {e}")
            # Fallback to API - fetch and filter manually
            api_contests = await self.api.fetch_upcoming_contests(days)

            # Apply platform filter if specified
            if platform and platform.lower() in self.platform_map:
                platform_name = None
                for name, key in {'Codeforces': 'codeforces.com', 'CodeChef': 'codechef.com',
                                  'AtCoder': 'atcoder.jp', 'LeetCode': 'leetcode.com'}.items():
                    if key == self.platform_map[platform.lower()]:
                        platform_name = name
                        break

                if platform_name:
                    api_contests = [
                        c for c in api_contests if c['platform'] == platform_name]
                    logging.info(
                        f"Filtered API results to {len(api_contests)} contests for {platform_name}")

            # Apply limit if specified
            if limit:
                api_contests = api_contests[:limit]

            return api_contests

    @app_commands.command(name="contests", description="Show upcoming programming contests (IST timezone)")
    @app_commands.describe(
        days='Number of days to look ahead (1-30, default: 3)',
        platform='Filter by platform (codeforces, codechef, atcoder, leetcode)',
        limit='Maximum number of contests to show (1-20, default: all)'
    )
    @app_commands.autocomplete(platform=platform_autocomplete)
    async def contests(self, interaction: discord.Interaction,
                       days: int = 3,
                       platform: Optional[str] = None,
                       limit: Optional[int] = None):
        """Show upcoming contests with optional filters."""
        # Validate inputs
        if days < 1 or days > 30:
            await interaction.response.send_message("❌ Days must be between 1 and 30.", ephemeral=True)
            return

        if limit and (limit < 1 or limit > 20):
            await interaction.response.send_message("❌ Limit must be between 1 and 20.", ephemeral=True)
            return

        if platform and platform.lower() not in self.platform_map:
            available = ", ".join(self.platform_map.keys())
            await interaction.response.send_message(f"❌ Invalid platform. Available: {available}", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            logging.info(
                f"Contest command: days={days}, platform={platform}, limit={limit}")
            contests = await self._get_contests_from_cache_or_api(platform, limit, days)
            logging.info(f"Retrieved {len(contests)} contests for display")

            if not contests:
                embed = discord.Embed(
                    title="📅 No Upcoming Contests",
                    description=f"No contests found in the next {days} day(s)" +
                    (f" for {platform}" if platform else "") + ".",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed)
                return

            # Group by platform
            platform_contests = {}
            for contest in contests:
                platform_name = contest.get('platform', 'Unknown')
                if platform_name not in platform_contests:
                    platform_contests[platform_name] = []
                platform_contests[platform_name].append(contest)

            embed = discord.Embed(
                title="🏆 Upcoming Programming Contests",
                description=f"Found **{len(contests)}** contest(s) in the next **{days}** day(s)" +
                (f" for **{platform}**" if platform else ""),
                color=0x3498db
            )

            for platform_name, contests_list in platform_contests.items():
                formatted = []
                display_limit = min(len(contests_list), 5)
                platform_emoji = self._get_emoji(contests_list[0].get('platform_key', '')) if contests_list else '⚪'

                for contest in contests_list[:display_limit]:
                    entry = (
                        f"**{contest['name']}**\n"
                        f"Start: {contest['start_time']}\n"
                        f"Duration: {contest.get('duration', 'Unknown')}"
                    )
                    if contest.get('url'):
                        entry += f"\n[Contest Link]({contest['url']})"
                    formatted.append(entry)

                if formatted:
                    embed.add_field(
                        name=f"{platform_emoji} {platform_name}",
                        value="\n\n".join(formatted),
                        inline=False
                    )

            embed.set_footer(text="All times in IST • Data from clist.by")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logging.error(f"Contest command error: {e}")
            # [Previous error handling code remains the same]
            embed = discord.Embed(
                title="❌ Contest Fetch Error",
                description="Unable to fetch contest information at the moment.",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="contests_today", description="Show contests starting today")
    @app_commands.describe(
        platform='Filter by platform (codeforces, codechef, atcoder, leetcode)',
        limit='Maximum number of contests to show (1-10, default: all)'
    )
    @app_commands.autocomplete(platform=platform_autocomplete)
    async def contests_today(self, interaction: discord.Interaction,
                             platform: Optional[str] = None,
                             limit: Optional[int] = None):
        """Show contests starting today."""
        if limit and (limit < 1 or limit > 10):
            await interaction.response.send_message("❌ Limit must be between 1 and 10.", ephemeral=True)
            return

        if platform and platform.lower() not in self.platform_map:
            available = ", ".join(self.platform_map.keys())
            await interaction.response.send_message(f"❌ Invalid platform. Available: {available}", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            platform_key = self.platform_map.get(
                platform.lower()) if platform else None

            # First try to use cached data
            contests = await self.bot.db.get_contests_today(platform=platform_key, limit=limit)
            data_source = "Data from clist.by"

            # If no cached data or cache is stale, fetch fresh data
            if not contests or await self.bot.db.is_cache_stale():
                try:
                    logging.info(
                        "Cache is stale or empty, fetching fresh today's contests...")
                    fresh_contests = await self.api.fetch_todays_contests()

                    # Filter by platform if specified
                    if platform_key:
                        platform_name = self.api._get_platform_name_from_key(
                            platform_key)
                        fresh_contests = [
                            c for c in fresh_contests if c['platform'] == platform_name]

                    # Apply limit if specified
                    if limit:
                        fresh_contests = fresh_contests[:limit]

                    contests = fresh_contests
                    data_source = "Fresh API data"
                except Exception as e:
                    logging.warning(f"Failed to fetch fresh data: {e}")
                    if not contests:  # Only show error if we have no fallback data
                        await interaction.followup.send("❌ Failed to fetch contest data. Please try again later.", ephemeral=True)
                        return

            embed = discord.Embed(
                title="📅 Today's Programming Contests",
                description="Real-time contest tracking with status updates",
                color=0x27ae60
            )

            if contests:
                contest_list = []
                for contest in contests:
                    try:
                        emoji = self._get_emoji(
                            contest.get('platform_key', ''))

                        # Get contest status and status emoji (with fallback for missing duration_seconds)
                        duration_seconds = contest.get('duration_seconds', 0)
                        status = self.api._get_contest_status(
                            contest['start_time'], duration_seconds)
                        status_emoji = self.api._get_status_emoji(status)

                        entry = f"{emoji} **{contest['name']}** {status_emoji}\n"
                        entry += f"Platform: {contest['platform']}\n"
                        entry += f"Start: {contest['start_time']}\n"
                        entry += f"Duration: {contest['duration']}"

                        if contest.get('url'):
                            entry += f"\n[Contest Link]({contest['url']})"

                        contest_list.append(entry)
                    except Exception as e:
                        logging.warning(
                            f"Error processing contest {contest.get('name', 'unknown')}: {e}")
                        # Add contest without status if there's an error
                        emoji = self._get_emoji(
                            contest.get('platform_key', ''))
                        entry = f"{emoji} **{contest['name']}**\n"
                        entry += f"Platform: {contest['platform']}\n"
                        entry += f"Start: {contest['start_time']}"
                        if contest.get('url'):
                            entry += f"\n[Contest Link]({contest['url']})"
                        contest_list.append(entry)

                embed.description = f"Found **{len(contests)}** contest(s) for today"
                embed.add_field(
                    name="Today's Schedule",
                    value="\n\n".join(contest_list),
                    inline=False
                )

                # Add status legend
                embed.add_field(
                    name="Status Legend",
                    value="⏰ Upcoming • 🔴 Running • ✅ Ended",
                    inline=False
                )
            else:
                embed.description = "No contests for today" + \
                    (f" on {platform}" if platform else "") + "."
                embed.color = 0xe74c3c

            embed.set_footer(text="All times in IST • Data from clist.by")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logging.error(f"Today's contests command error: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Unable to fetch today's contests.",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="contests_tomorrow", description="Show contests starting tomorrow")
    @app_commands.describe(
        platform='Filter by platform (codeforces, codechef, atcoder, leetcode)',
        limit='Maximum number of contests to show (1-10, default: all)'
    )
    @app_commands.autocomplete(platform=platform_autocomplete)
    async def contests_tomorrow(self, interaction: discord.Interaction,
                                platform: Optional[str] = None,
                                limit: Optional[int] = None):
        """Show contests starting tomorrow."""
        if limit and (limit < 1 or limit > 10):
            await interaction.response.send_message("❌ Limit must be between 1 and 10.", ephemeral=True)
            return

        if platform and platform.lower() not in self.platform_map:
            available = ", ".join(self.platform_map.keys())
            await interaction.response.send_message(f"❌ Invalid platform. Available: {available}", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            platform_key = self.platform_map.get(
                platform.lower()) if platform else None
            contests = await self.bot.db.get_contests_tomorrow(platform=platform_key, limit=limit)

            embed = discord.Embed(
                title="🌅 Tomorrow's Programming Contests",
                description="Plan ahead with tomorrow's contest schedule",
                color=0x3498db
            )

            if contests:
                contest_list = []
                for contest in contests:
                    emoji = self._get_emoji(contest.get('platform_key', ''))
                    entry = f"{emoji} **{contest['name']}**\n"
                    entry += f"Platform: {contest['platform']}\n"
                    entry += f"Start: {contest['start_time']}\n"
                    entry += f"Duration: {contest.get('duration', 'Unknown')}"
                    if contest.get('url'):
                        entry += f"\n[Contest Link]({contest['url']})"
                    contest_list.append(entry)

                embed.description = f"Found **{len(contests)}** contest(s) starting tomorrow"
                embed.add_field(
                    name="Tomorrow's Schedule",
                    value="\n\n".join(contest_list),
                    inline=False
                )
            else:
                embed.description = "No contests starting tomorrow" + \
                    (f" for {platform}" if platform else "") + "."
                embed.color = 0xe74c3c

            embed.set_footer(text="All times in IST • Data from clist.by")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logging.error(f"Tomorrow's contests command error: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Unable to fetch tomorrow's contests.",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="contest_setup", description="Set contest announcement channel")
    @app_commands.describe(
        channel_id='Channel for contest announcements (default: current channel)'
    )
    @app_commands.autocomplete(channel_id=channel_autocomplete)
    async def contest_setup(self, interaction: discord.Interaction, channel_id: Optional[str] = None):
        """Set up contest announcement channel."""
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        # Check if user has admin permissions
        if not is_admin(interaction):
            await interaction.response.send_message("❌ Administrator permission or server ownership required.", ephemeral=True)
            return

        logging.info(f"Contest setup command used by {interaction.user}")

        # Get target channel
        if channel_id:
            try:
                target_channel = interaction.guild.get_channel(int(channel_id))
                if not target_channel or not isinstance(target_channel, discord.TextChannel):
                    await interaction.response.send_message("❌ Invalid channel ID or not a text channel.", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("❌ Invalid channel ID format.", ephemeral=True)
                return
        else:
            target_channel = interaction.channel
            if not isinstance(target_channel, discord.TextChannel):
                await interaction.response.send_message("❌ Current channel is not a text channel.", ephemeral=True)
                return

        # Check bot permissions
        permissions = target_channel.permissions_for(interaction.guild.me)
        if not (permissions.send_messages and permissions.embed_links):
            await interaction.response.send_message(
                f"❌ I need Send Messages and Embed Links permissions in {target_channel.mention}",
                ephemeral=True
            )
            return

        # Save to database
        await self.bot.db.set_contest_channel(interaction.guild.id, target_channel.id)
        logging.info(
            f"Contest channel set to {target_channel.name} for guild {interaction.guild.name}")

        embed = discord.Embed(
            title="✅ Contest Channel Configured",
            description=f"Contest announcements will be sent to {target_channel.mention}",
            color=0x27ae60
        )
        await interaction.response.send_message(embed=embed)

        # Send test message
        test_embed = discord.Embed(
            title="🎯 Contest Channel Ready",
            description="This channel is now configured for contest announcements!",
            color=0x3498db
        )
        await target_channel.send(embed=test_embed)

    @app_commands.command(name="contest_time", description="Set daily announcement time")
    @app_commands.describe(time='Time in HH:MM format (24-hour, IST, default: 09:00)')
    async def contest_time(self, interaction: discord.Interaction, time: str = "09:00"):
        """Set daily contest announcement time."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        if not is_admin(interaction):
            await interaction.response.send_message("❌ Administrator permission or server ownership required.", ephemeral=True)
            return

        # Validate time format
        try:
            datetime.strptime(time, '%H:%M')
        except ValueError:
            await interaction.response.send_message("❌ Invalid time format. Use HH:MM (24-hour format).", ephemeral=True)
            return

        # Save to database
        await self.bot.db.set_announcement_time(interaction.guild.id, time)

        embed = discord.Embed(
            title="⏰ Announcement Time Set",
            description=f"Daily contest announcements will be sent at **{time} IST**",
            color=0x27ae60
        )
        embed.add_field(
            name="📝 Note",
            value="Make sure you've set a contest channel using `/contest_setup` first!",
            inline=False
        )
        embed.set_footer(text="🕐 Time zone: IST (Indian Standard Time)")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="refresh_contests", description="[Admin] Manually refresh contest cache")
    async def refresh_contests(self, interaction: discord.Interaction):
        """Admin command to manually refresh contest cache."""
        # Check if user is admin
        if not is_admin(interaction):
            await interaction.response.send_message("❌ You need admin permissions to use this command.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            embed = discord.Embed(
                title="🔄 Refreshing Contest Cache",
                description="Fetching latest contest data...",
                color=0xf39c12
            )
            await interaction.followup.send(embed=embed)

            # Fetch and cache contests
            cached_count = await self.bot.db.fetch_and_cache_contests(self.api, max_days=30)

            # Success embed
            success_embed = discord.Embed(
                title="✅ Contest Cache Refreshed",
                description=f"Successfully cached {cached_count} contests for the next 30 days",
                color=0x27ae60
            )
            success_embed.add_field(
                name="📊 Cache Status",
                value=f"• **Contests Cached**: {cached_count}\n• **Coverage**: 30 days\n• **Last Updated**: Just now",
                inline=False
            )
            success_embed.set_footer(
                text="Use /contests to see the latest data")

            await interaction.edit_original_response(embed=success_embed)
            logging.info(
                f"Manual contest cache refresh by {interaction.user} - cached {cached_count} contests")

        except Exception as e:
            logging.error(f"Manual contest refresh error: {e}")
            error_embed = discord.Embed(
                title="❌ Cache Refresh Failed",
                description="Unable to refresh contest cache. Please try again later.",
                color=0xe74c3c
            )
            await interaction.edit_original_response(embed=error_embed)


async def setup(bot):
    """Load the contest feature."""
    await bot.add_cog(ContestCommands(bot))
