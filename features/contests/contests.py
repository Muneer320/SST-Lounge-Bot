"""
Contest Feature Module
Complete contest functionality for SST Lounge Discord Server.
Handles contest fetching, announcements, and user commands.
"""

import os
import logging
import aiohttp
import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import discord
from discord.ext import commands
from discord import app_commands

# Import the admin check function
from features.admin.admin import is_admin


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

            # Time range in UTC for API
            start_time = datetime.now(pytz.timezone(
                'Asia/Kolkata')).replace(tzinfo=pytz.UTC)
            end_time = start_time + timedelta(days=days)

            params = {
                'start__gte': start_time.isoformat(),
                'start__lte': end_time.isoformat(),
                'resource__in': ','.join(self.platforms),
                'order_by': 'start',
                'format': 'json'
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

                # Format duration
                duration_seconds = contest.get('duration', 0)
                duration_str = self._format_duration(duration_seconds)

                processed.append({
                    'name': contest['event'],
                    'platform': platform_names.get(contest['resource'], contest['resource']),
                    'start_time': ist_time.strftime('%B %d, %Y at %I:%M %p IST'),
                    'duration': duration_str,
                    'url': contest.get('href', ''),
                    'platform_emoji': self._get_emoji(contest['resource'])
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
            'codeforces.com': '🔴',
            'codechef.com': '🟤',
            'atcoder.jp': '🟠',
            'leetcode.com': '🟡'
        }
        return emojis.get(platform, '⚪')


class ContestCommands(commands.Cog):
    """Contest-related slash commands."""

    def __init__(self, bot):
        self.bot = bot
        self.api = ContestAPI()

    async def cog_unload(self):
        await self.api.close()

    @app_commands.command(name="contests", description="Show upcoming programming contests (IST timezone)")
    @app_commands.describe(days='Number of days to look ahead (1-14, default: 3)')
    async def contests(self, interaction: discord.Interaction, days: int = 3):
        """Show upcoming contests."""
        if days < 1 or days > 14:
            await interaction.response.send_message("❌ Days must be between 1 and 14.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            contests = await self.api.fetch_upcoming_contests(days)

            if not contests:
                embed = discord.Embed(
                    title="📅 No Upcoming Contests",
                    description=f"No contests found in the next {days} day(s).",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed)
                return

            # Group by platform
            platform_contests = {}
            for contest in contests:
                platform = contest['platform']
                if platform not in platform_contests:
                    platform_contests[platform] = []
                platform_contests[platform].append(contest)

            embed = discord.Embed(
                title="🏆 Upcoming Programming Contests",
                description=f"Found {len(contests)} contest(s) in the next {days} day(s)",
                color=0x00ff00
            )

            for platform, contests_list in platform_contests.items():
                formatted = []
                # show up to 5 contests per platform
                for contest in contests_list[:5]:
                    entry = (
                        f"• **{contest['name']}**\n"
                        f"    🕒 {contest['start_time']}\n"
                        f"    ⏱️ {contest['duration']}"
                    )
                    if contest.get('url'):
                        entry += f"\n    🔗 [Link]({contest['url']})"
                    formatted.append(entry)

                if formatted:
                    embed.add_field(
                        name=f"**{contests_list[0]['platform_emoji']} {platform}**",
                        value="\n\n".join(formatted),
                        inline=False
                    )

            embed.set_footer(text="All times in IST • Data from clist.by")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logging.error(f"Contest command error: {e}")

            # Handle specific API errors
            if str(e) == "API_UNAUTHORIZED":
                embed = discord.Embed(
                    title="🔐 API Authentication Error",
                    description="The contest API requires authentication that hasn't been configured.",
                    color=0xe74c3c
                )
                embed.add_field(
                    name="What this means",
                    value="• The clist.by API returned a 401 Unauthorized error\n• API credentials are missing or invalid",
                    inline=False
                )
                embed.add_field(
                    name="Solution",
                    value="• Contact an administrator to configure API credentials\n• The bot can work without API but with limited contest data",
                    inline=False
                )
            elif str(e) == "API_RATE_LIMITED":
                embed = discord.Embed(
                    title="⏱️ Rate Limited",
                    description="Too many requests to the contest API. Please wait before trying again.",
                    color=0xf39c12
                )
            elif str(e).startswith("API_ERROR_"):
                status_code = str(e).split("_")[-1]
                embed = discord.Embed(
                    title=f"🚫 API Error {status_code}",
                    description="The contest API returned an error.",
                    color=0xe74c3c
                )
            else:
                embed = discord.Embed(
                    title="❌ Contest Fetch Error",
                    description="Unable to fetch contest information at the moment.",
                    color=0xe74c3c
                )
                embed.add_field(
                    name="Possible Issues",
                    value="• Network connectivity issues\n• API service temporarily unavailable\n• Server configuration issues",
                    inline=False
                )

            embed.add_field(
                name="What to do",
                value="Please try again in a few minutes. If the issue persists, contact an administrator.",
                inline=False
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="contest_setup", description="Set contest announcement channel")
    @app_commands.describe(channel='Channel for contest announcements (default: current channel)')
    async def contest_setup(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
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

        target_channel = channel or interaction.channel

        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("❌ Please specify a valid text channel.", ephemeral=True)
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


async def setup(bot):
    """Load the contest feature."""
    await bot.add_cog(ContestCommands(bot))
