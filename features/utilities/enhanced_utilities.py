"""
Test Enhancement: Enhanced Help Command
This is a minor test change to demonstrate CI/CD workflows.
"""

import discord
from discord.ext import commands
from discord import app_commands


class EnhancedUtilityCommands(commands.Cog):
    """Enhanced utility commands for SST Lounge with better formatting."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help_enhanced", description="Show enhanced help with better formatting")
    async def help_enhanced(self, interaction: discord.Interaction):
        """Enhanced help command with emoji indicators."""

        embed = discord.Embed(
            title="🤖 SST Lounge Bot - Enhanced Help",
            description="Comprehensive Discord bot for SST Batch '29",
            color=0x3498db
        )

        # Contest Commands
        embed.add_field(
            name="🏆 Contest Commands",
            value=(
                "• `/contests` - Upcoming programming contests\n"
                "• `/contests_today` - Today's contests with status\n"
                "• `/contests_tomorrow` - Tomorrow's contests"
            ),
            inline=False
        )

        # Utility Commands
        embed.add_field(
            name="🛠️ Utility Commands",
            value=(
                "• `/ping` - Check bot response time\n"
                "• `/hello` - Friendly bot greeting\n"
                "• `/contribute` - Contribution guidelines"
            ),
            inline=False
        )

        # Admin Commands
        embed.add_field(
            name="⚙️ Admin Commands",
            value=(
                "• `/refresh_contests` - Manual cache refresh\n"
                "• `/contest_setup` - Configure announcements\n"
                "• `/update` - Update bot from GitHub"
            ),
            inline=False
        )

        embed.set_footer(
            text="SST Lounge Bot v1.4.0 | For SST Batch '29",
            icon_url="https://cdn.discordapp.com/icons/your-server-id/your-icon.png"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the enhanced utility commands."""
    await bot.add_cog(EnhancedUtilityCommands(bot))
