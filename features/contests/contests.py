"""
Contest Feature Module
Complete contest functionality for SST Lounge Discord Server.
Handles contest fetching, announcements, and user commands.
"""

import logging
import aiohttp
import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import discord
from discord.ext import commands
from discord import app_commands


class ContestAPI:
    """Handles contest data fetching from clist.by API."""

    def __init__(self):
        self.base_url = "https://clist.by/api/v4/contest/"
        self.platforms = ['codeforces.com',
                          'codechef.com', 'atcoder.jp', 'leetcode.com']
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch_upcoming_contests(self, days: int = 7) -> List[Dict]:
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

            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_contests(data.get('objects', []))
                else:
                    logging.error(f"API Error: {response.status}")
                    return []

        except Exception as e:
            logging.error(f"Contest fetch error: {e}")
            return []

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
    @app_commands.describe(days='Number of days to look ahead (1-14, default: 7)')
    async def contests(self, interaction: discord.Interaction, days: int = 7):
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
            for contest in contests[:10]:  # Limit to 10
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
                contest_text = []
                for contest in contests_list[:3]:  # Max 3 per platform
                    text = f"**{contest['name']}**\n"
                    text += f"🕒 {contest['start_time']}\n"
                    text += f"⏱️ {contest['duration']}"
                    if contest['url']:
                        text += f"\n🔗 [Link]({contest['url']})"
                    contest_text.append(text)

                if contest_text:
                    field_value = '\n\n'.join(contest_text)
                    embed.add_field(
                        name=f"{contests_list[0]['platform_emoji']} {platform}",
                        value=field_value,
                        inline=False
                    )

            embed.set_footer(text="All times in IST • Data from clist.by")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logging.error(f"Contest command error: {e}")
            await interaction.followup.send("❌ Failed to fetch contests. Please try again later.", ephemeral=True)

    @app_commands.command(name="contest_setup", description="Set contest announcement channel")
    @app_commands.describe(channel='Channel for contest announcements (default: current channel)')
    async def contest_setup(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Set up contest announcement channel."""
        # Check if user has admin permissions
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        member = interaction.guild.get_member(interaction.user.id)
        if not member or not member.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permission required.", ephemeral=True)
            return

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
