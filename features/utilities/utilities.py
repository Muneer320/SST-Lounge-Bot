"""
Utility Commands for SST Lounge
Basic utility commands and bot information.
"""

import discord
from discord.ext import commands
from discord import app_commands


class UtilityCommands(commands.Cog):
    """Basic utility commands for SST Lounge."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot response time")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency."""
        latency = round(self.bot.latency * 1000)
        color = 0x00ff00 if latency < 100 else 0xffff00 if latency < 200 else 0xff0000

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=color
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hello", description="Say hello to the SST Lounge bot")
    async def hello(self, interaction: discord.Interaction):
        """Greet the user."""
        embed = discord.Embed(
            title="👋 Hello SST Batch '29!",
            description=f"Hey {interaction.user.mention}! I'm the SST Lounge bot here to help our batch!",
            color=0x3498db
        )
        embed.add_field(
            name="🎯 What I Do",
            value="I help with contest notifications, server management, and batch coordination!",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        """Show bot help."""
        embed = discord.Embed(
            title="📚 SST Lounge Bot Commands",
            description="Here are all available commands for our batch:",
            color=0x3498db
        )

        embed.add_field(
            name="🏆 Contest Commands",
            value="• `/contests [days] [platform] [limit]` - Show upcoming contests\n"
                  "• `/contests_today [platform] [limit]` - Show today's contests\n"
                  "• `/contests_tomorrow [platform] [limit]` - Show tomorrow's contests",
            inline=False
        )

        embed.add_field(
            name="🎭 Role Commands",
            value="• `/veteran_info` - Show Discord Veteran role criteria\n"
                  "• `/check_veterans` - Check veteran roles (Admin only)",
            inline=False
        )

        embed.add_field(
            name="🔧 Utility Commands",
            value="• `/ping` - Check bot response time\n"
                  "• `/hello` - Say hello\n"
                  "• `/help` - Show this help",
            inline=False
        )

        embed.add_field(
            name="⚙️ Admin Commands",
            value="• `/info` - Show bot information\n"
                  "• `/sync` - Sync slash commands\n"
                  "• `/grant_admin [user/role]` - Grant bot admin privileges (Owner only)\n"
                  "• `/revoke_admin [user/role]` - Revoke bot admin privileges (Owner only)\n"
                  "• `/list_admins` - List all bot admins",
            inline=False
        )

        embed.add_field(
            name="🏗️ Contest Setup (Admin)",
            value="• `/contest_setup [channel]` - Set contest channel\n"
                  "• `/contest_time [time]` - Set announcement time\n"
                  "• `/refresh_contests` - Refresh contest cache",
            inline=False
        )

        embed.set_footer(text="SST Lounge Bot • All contest times in IST")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the utility commands."""
    await bot.add_cog(UtilityCommands(bot))
