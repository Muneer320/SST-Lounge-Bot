"""
Help Command View System
Interactive buttons for help command responses.
"""

import discord
from utils.version import get_bot_name


class HelpView(discord.ui.View):
    """Interactive buttons for help command responses."""

    def __init__(self, bot=None):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.bot = bot

    @discord.ui.button(label="Contest Commands", style=discord.ButtonStyle.primary, emoji="🏆")
    async def contest_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed contest command information."""
        embed = discord.Embed(
            title="🏆 Contest Commands - Detailed Guide",
            description="Track programming contests across multiple platforms",
            color=0xe74c3c
        )

        embed.add_field(
            name="📅 Main Commands",
            value="**`/contests [days] [platform] [limit]`**\n"
                  "• **days**: 1-30 days ahead (default: 3)\n"
                  "• **platform**: Filter by specific platform\n"
                  "• **limit**: Max results 1-20 (default: all)\n\n"
                  "**`/contests_today [platform] [limit]`**\n"
                  "• Shows today's contests with live status\n"
                  "• Real-time status indicators\n\n"
                  "**`/contests_tomorrow [platform] [limit]`**\n"
                  "• Tomorrow's scheduled contests",
            inline=False
        )

        embed.add_field(
            name="🎯 Supported Platforms",
            value="🔵 **Codeforces** (`codeforces`)\n"
                  "🟡 **CodeChef** (`codechef`)\n"
                  "🟠 **AtCoder** (`atcoder`)\n"
                  "🟢 **LeetCode** (`leetcode`)",
            inline=True
        )

        embed.add_field(
            name="📊 Status Indicators",
            value="⏰ **Upcoming** - Not started yet\n"
                  "🔴 **Running** - Currently active\n"
                  "✅ **Ended** - Contest finished\n"
                  "🕒 **All times in IST**",
            inline=True
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Utility Commands", style=discord.ButtonStyle.secondary, emoji="🛠️")
    async def utility_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show utility command information."""
        embed = discord.Embed(
            title="🛠️ Utility Commands - Quick Reference",
            description="Essential bot functionality and information",
            color=0x3498db
        )

        embed.add_field(
            name="🔧 Basic Commands",
            value="**`/ping`** - Check bot response time and latency\n"
                  "**`/hello`** - Friendly greeting from the bot\n"
                  "**`/help`** - Show this interactive command guide\n"
                  "**`/contribute`** - Get contribution guidelines and GitHub link",
            inline=False
        )

        embed.add_field(
            name="💡 Pro Tips",
            value="• Use `/admin_help` if you're a bot administrator\n"
                  "• All commands use modern slash command interface\n"
                  "• Most commands support filtering and options\n"
                  "• Bot automatically updates data daily at midnight IST",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Role Management", style=discord.ButtonStyle.secondary, emoji="🎭")
    async def role_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show role management information."""
        embed = discord.Embed(
            title="🎭 Role Management - Discord Veteran System",
            description="Automatic role assignment based on Discord account age",
            color=0x9b59b6
        )

        embed.add_field(
            name="📋 Available Commands",
            value="**`/veteran_info`** - Check your qualification status for Discord Veteran role\n"
                  "• Shows your Discord account creation date\n"
                  "• Displays if you qualify for the veteran role\n"
                  "• Explains the criteria for automatic assignment",
            inline=False
        )

        embed.add_field(
            name="✨ Automatic Features",
            value="🔄 **Daily Checks** - Bot checks all members daily\n"
                  "🎯 **Auto Assignment** - 5+ year accounts get veteran role\n"
                  "🚪 **Join Detection** - New members checked immediately\n"
                  "⚙️ **Smart Creation** - Role created automatically if missing",
            inline=False
        )

        embed.add_field(
            name="📊 Qualification Criteria",
            value="**Discord Veteran Role Requirements:**\n"
                  "• Discord account must be **5+ years old**\n"
                  "• Automatic assignment upon qualification\n"
                  "• No manual application required",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Admin Commands", style=discord.ButtonStyle.danger, emoji="⚙️")
    async def admin_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show admin command information."""
        # Import here to avoid circular imports
        from features.admin.admin import is_admin

        if not self.bot or not await is_admin(interaction, self.bot):
            await interaction.response.send_message(
                "❌ **Admin Access Required**\n\n"
                "This section is only available to bot administrators.\n"
                "Contact a server owner if you need admin access.\n\n"
                "**Current Admin Levels:**\n"
                "• Server Owner (automatic access)\n"
                "• Discord Administrators\n"
                "• Bot Admins (granted by owner)",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚙️ Admin Commands - Control Panel",
            description="Administrative commands for bot management",
            color=0xe74c3c
        )

        embed.add_field(
            name="🤖 Bot Administration",
            value="**`/info`** - Bot statistics and server information\n"
                  "**`/sync`** - Sync slash commands with Discord\n"
                  "**`/update`** - Update bot from GitHub repository\n"
                  "**`/list_admins`** - Show all bot administrators\n"
                  "**`/logs`** - Export bot logs as downloadable file",
            inline=False
        )

        embed.add_field(
            name="🏆 Contest Management",
            value="**`/contest_setup`** - Set contest announcement channel\n"
                  "**`/contest_time`** - Configure daily announcement time\n"
                  "**`/refresh_contests`** - Manually refresh contest cache",
            inline=False
        )

        embed.add_field(
            name="👑 Owner Only Commands",
            value="**`/grant_admin`** - Grant bot admin privileges\n"
                  "**`/revoke_admin`** - Remove bot admin privileges\n"
                  "**`/check_veterans`** - Manual veteran role check\n\n"
                  "*These commands require server owner permissions*",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class AdminHelpView(discord.ui.View):
    """Interactive buttons for admin help command responses."""

    def __init__(self, bot=None):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.bot = bot

    @discord.ui.button(label="Bot Management", style=discord.ButtonStyle.primary, emoji="🤖")
    async def bot_management_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed bot management commands."""
        embed = discord.Embed(
            title="🤖 Bot Management - Detailed Guide",
            description="System administration and monitoring commands",
            color=0x3498db
        )

        embed.add_field(
            name="📊 System Information",
            value="**`/info`** - Comprehensive bot statistics\n"
                  "• Server count and member statistics\n"
                  "• Bot latency and performance metrics\n"
                  "• Version information and uptime\n"
                  "• Database status and cache information",
            inline=False
        )

        embed.add_field(
            name="🔧 System Control",
            value="**`/sync`** - Synchronize slash commands\n"
                  "• Updates command list with Discord\n"
                  "• Use after adding new commands\n\n"
                  "**`/update`** - Update bot from GitHub\n"
                  "• Checks for new version automatically\n"
                  "• Interactive confirmation required\n"
                  "• Automatic restart after update",
            inline=False
        )

        embed.add_field(
            name="📋 Logging & Monitoring",
            value="**`/logs [options]`** - Export bot logs\n"
                  "• Filter by time (hours/minutes)\n"
                  "• Filter by log level (INFO/WARNING/ERROR/DEBUG)\n"
                  "• Export up to 1000 lines\n"
                  "• Download as organized text file",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Contest Settings", style=discord.ButtonStyle.secondary, emoji="🏆")
    async def contest_settings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show contest management commands."""
        embed = discord.Embed(
            title="🏆 Contest Management - Configuration Guide",
            description="Configure automated contest announcements and data management",
            color=0xe74c3c
        )

        embed.add_field(
            name="📢 Announcement Setup",
            value="**`/contest_setup [channel]`** - Set announcement channel\n"
                  "• Configure where daily contest announcements are posted\n"
                  "• Bot will automatically post at configured time\n"
                  "**`/contest_time [time]`** - Set announcement time\n"
                  "• Format: HH:MM in 24-hour format (IST timezone)\n"
                  "• Default time is 09:00 IST\n"
                  "• Announcements include today's and upcoming contests",
            inline=False
        )

        embed.add_field(
            name="🔄 Data Management",
            value="**`/refresh_contests`** - Manual cache refresh\n"
                  "• Immediately update contest data from API\n"
                  "• Bypasses normal daily refresh cycle\n"
                  "• Use when contest data seems outdated\n"
                  "• Takes 5-10 seconds to complete",
            inline=False
        )

        embed.add_field(
            name="⚙️ Automatic Features",
            value="• **Daily Refresh**: Every day at 00:00 IST\n"
                  "• **Smart Caching**: 30-day contest data cached locally\n"
                  "• **Platform Support**: Codeforces, CodeChef, AtCoder, LeetCode\n"
                  "• **Status Detection**: Real-time contest status updates",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Owner Commands", style=discord.ButtonStyle.danger, emoji="👑")
    async def owner_commands_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show owner-only commands."""
        embed = discord.Embed(
            title="👑 Owner Commands - Privilege Management",
            description="Commands restricted to Discord server owners",
            color=0x992d22
        )

        embed.add_field(
            name="🛡️ Admin Privilege Management",
            value="**`/grant_admin [user/role]`** - Grant bot admin privileges\n"
                  "• Grant to specific user: `/grant_admin user:@username`\n"
                  "• Grant to entire role: `/grant_admin role:@rolename`\n"
                  "• Bot-level privileges independent of Discord permissions\n\n"
                  "**`/revoke_admin [user/role]`** - Remove bot admin privileges\n"
                  "• Same syntax as grant command\n"
                  "• Immediately removes all bot admin access\n"
                  "• Does not affect Discord server permissions",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
