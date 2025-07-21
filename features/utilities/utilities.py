"""
Utility Commands for SST Lounge
Basic utility commands and bot information.
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.version import get_bot_name, get_bot_description, get_repository_url
from datetime import datetime, timedelta
from typing import Optional

# Import the admin check function
from features.admin.admin import is_admin

# Autocomplete functions
async def log_level_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    return [
        app_commands.Choice(name=level, value=level)
        for level in levels if current.upper() in level
    ]


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

    @app_commands.command(name="hello", description=f"Say hello to the {get_bot_name()}")
    async def hello(self, interaction: discord.Interaction):
        """Greet the user."""
        embed = discord.Embed(
            title="👋 Hello SST Batch '29!",
            description=f"Hey {interaction.user.mention}! I'm the {get_bot_name()} here to help our batch!",
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
        """Show basic bot help with user commands."""
        embed = discord.Embed(
            title="🤖 SST Lounge Bot - Command Guide",
            description="**Discord bot for SST Batch '29**\n\n## 📋 Available Commands",
            color=0x3498db
        )

        # Contest Commands
        embed.add_field(
            name="🏆 Contest Commands",
            value="**View programming contests and schedules**\n"
                  "```\n"
                  "/contests            → Show upcoming contests\n"
                  "/contests_today      → Today's contests with status\n"
                  "/contests_tomorrow   → Tomorrow's contests\n"
                  "```\n"
                  "**Supported Platforms:** `codeforces` `codechef` `atcoder` `leetcode`",
            inline=False
        )

        # Utility Commands  
        embed.add_field(
            name="🛠️ Utility Commands",
            value="**Bot utilities and information**\n"
                  "```\n"
                  "/ping        → Check bot response time\n"
                  "/hello       → Friendly bot greeting\n"
                  "/help        → Show this command guide\n"
                  "/contribute  → Contribution guidelines\n"
                  "```",
            inline=False
        )

        # Role Commands
        embed.add_field(
            name="🎭 Role Management",
            value="**Discord server role utilities**\n"
                  "```\n"
                  "/veteran_info → Show role criteria\n"
                  "```",
            inline=False
        )

        embed.add_field(
            name="💡 Tips & Information",
            value="• All contest times displayed in **IST** timezone\n"
                  "• Status indicators: ⏰ *Upcoming* | 🔴 *Running* | ✅ *Ended*\n"
                  "• Use filters to find contests for specific platforms\n"
                  "• Bot automatically refreshes contest data daily\n"
                  "• Type `/admin_help` if you're an administrator",
            inline=False
        )

        embed.set_footer(
            text=f"{get_bot_name()} | Made for SST Batch '29 | Type /contribute for development info"
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="admin_help", description="Show admin commands (Admin only)")
    async def admin_help(self, interaction: discord.Interaction):
        """Show admin commands - only visible to admins."""
        if not is_admin(interaction):
            await interaction.response.send_message("❌ You need admin permissions to use this command.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"⚙️ {get_bot_name()} - Admin Commands",
            description="**Administrative commands for SST Batch '29**\n\n## 🔧 Admin Control Panel",
            color=0xe74c3c
        )

        # Bot Administration
        embed.add_field(
            name="🤖 Bot Administration",
            value="**System management and monitoring**\n"
                  "```\n"
                  "/info             → Bot statistics & info\n"
                  "/sync             → Sync slash commands\n"
                  "/update           → Update bot from GitHub\n"
                  "/list_admins      → Show all bot admins\n"
                  "/logs             → View bot logs\n"
                  "```",
            inline=False
        )

        # Contest Management
        embed.add_field(
            name="🏆 Contest Management",
            value="**Configure contest announcements**\n"
                  "```\n"
                  "/contest_setup      → Set announcement channel\n"
                  "/contest_time       → Set daily announcement time\n"
                  "/refresh_contests   → Manual cache refresh\n"
                  "```",
            inline=False
        )

        # Role Management
        embed.add_field(
            name="🎭 Role Management",
            value="**Manage server roles and permissions**\n"
                  "```\n"
                  "/check_veterans     → Manual veteran role check\n"
                  "```",
            inline=False
        )

        # Owner Only Commands
        embed.add_field(
            name="👑 Owner Only Commands",
            value="**Restricted to bot owner only**\n"
                  "```\n"
                  "/grant_admin        → Grant admin permissions\n"
                  "/revoke_admin       → Revoke admin permissions\n"
                  "```",
            inline=False
        )

        embed.add_field(
            name="📋 Administrator Guidelines",
            value="• Use `/contest_setup` before setting announcement times\n"
                  "• Check bot logs regularly for any issues\n"
                  "• Contest cache refreshes automatically every 6 hours\n"
                  "• Use `/sync` if slash commands aren't appearing\n"
                  "• Use `/logs` command to monitor bot activity",
            inline=False
        )

        embed.set_footer(
            text=f"Admin Panel | {get_bot_name()} | Handle with care!"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="logs", description="Export bot logs as file (Admin only)")
    @app_commands.describe(
        lines="Number of lines to show (default: 50, max: 1000)",
        hours="Show logs from last N hours (overrides lines)",
        minutes="Show logs from last N minutes (overrides lines and hours)",
        level="Filter by log level (INFO, WARNING, ERROR, DEBUG)"
    )
    @app_commands.autocomplete(level=log_level_autocomplete)
    async def logs(self, interaction: discord.Interaction, 
                   lines: Optional[int] = 50, 
                   hours: Optional[int] = None,
                   minutes: Optional[int] = None,
                   level: Optional[str] = None):
        """Export bot logs as downloadable file - admin only command."""
        if not is_admin(interaction):
            await interaction.response.send_message("❌ You need admin permissions to use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Validate parameters
            if lines and (lines < 1 or lines > 1000):
                await interaction.followup.send("❌ Lines must be between 1 and 1000.", ephemeral=True)
                return

            if hours and hours < 1:
                await interaction.followup.send("❌ Hours must be a positive number.", ephemeral=True)
                return

            if minutes and minutes < 1:
                await interaction.followup.send("❌ Minutes must be a positive number.", ephemeral=True)
                return

            if level and level.upper() not in ['INFO', 'WARNING', 'ERROR', 'DEBUG']:
                await interaction.followup.send("❌ Level must be one of: INFO, WARNING, ERROR, DEBUG", ephemeral=True)
                return

            # Find log file
            log_file = None
            possible_paths = [
                'features/logs/sst_lounge.log',
                'logs/sst_lounge.log',
                'sst_lounge.log',
                'bot.log',
                'logs/bot.log'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    log_file = path
                    break
            
            if not log_file:
                await interaction.followup.send("❌ Log file not found. Check bot configuration.", ephemeral=True)
                return

            # Read log file
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()

            if not all_lines:
                await interaction.followup.send("📝 Log file is empty.", ephemeral=True)
                return

            # Filter by time if specified
            filtered_lines = []
            time_desc = "recent entries"  # Default description
            
            if minutes or hours:
                cutoff_time = datetime.now()
                if minutes:
                    cutoff_time -= timedelta(minutes=minutes)
                    time_desc = f"last {minutes} minute(s)"
                elif hours:
                    cutoff_time -= timedelta(hours=hours)
                    time_desc = f"last {hours} hour(s)"

                for line in all_lines:
                    try:
                        # Extract timestamp from log line (assuming format: YYYY-MM-DD HH:MM:SS,mmm)
                        if len(line) > 19:
                            timestamp_str = line[:19]
                            log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            if log_time >= cutoff_time:
                                filtered_lines.append(line)
                    except (ValueError, IndexError):
                        # If we can't parse timestamp, include the line anyway
                        filtered_lines.append(line)
                
                log_lines = filtered_lines
                if not log_lines:
                    await interaction.followup.send(f"📝 No logs found in the {time_desc}.", ephemeral=True)
                    return
            else:
                # Use last N lines
                lines = lines or 50  # Ensure lines is not None
                log_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                time_desc = f"most recent {len(log_lines)} entries"

            # Filter by log level if specified
            if level:
                level_upper = level.upper()
                log_lines = [line for line in log_lines if f" - {level_upper} - " in line]
                if not log_lines:
                    await interaction.followup.send(f"📝 No {level_upper} logs found in the {time_desc}.", ephemeral=True)
                    return

            # Prepare log content
            log_content = ''.join(log_lines)
            
            # Create file content with header
            file_content = f"=== Bot Logs Export ===\n"
            file_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            file_content += f"Time Range: {time_desc}\n"
            if level:
                file_content += f"Log Level: {level.upper()}\n"
            file_content += f"Total Lines: {len(log_lines)}\n"
            file_content += f"Source File: {log_file}\n"
            file_content += "=" * 50 + "\n\n"
            file_content += log_content

            # Create a file-like object
            import io
            file_buffer = io.BytesIO(file_content.encode('utf-8'))
            
            # Generate filename with timestamp and filters
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_parts = ['logs', timestamp]
            if level:
                filename_parts.append(level)
            if minutes:
                filename_parts.append(f'{minutes}min')
            elif hours:
                filename_parts.append(f'{hours}hr')
            filename = '_'.join(filename_parts) + '.txt'
            
            # Create Discord file object
            discord_file = discord.File(file_buffer, filename=filename)
            
            # Send confirmation message with file
            await interaction.followup.send(
                content=f"� **Bot Logs Export**\n"
                        f"🕒 **Time Range:** {time_desc}\n"
                        f"📊 **Total Lines:** {len(log_lines)}\n"
                        f"📁 **File:** `{filename}`" + 
                        (f"\n🔍 **Level Filter:** {level.upper()}" if level else ""),
                file=discord_file,
                ephemeral=True
            )

        except FileNotFoundError:
            await interaction.followup.send("❌ Log file not found.", ephemeral=True)
        except PermissionError:
            await interaction.followup.send("❌ Permission denied reading log file.", ephemeral=True)
        except Exception as e:
            logging.error(f"Error in logs command: {e}")
            await interaction.followup.send(f"❌ Error reading logs: {str(e)}", ephemeral=True)

    @app_commands.command(name="contribute", description="Get information about contributing to the bot")
    async def contribute(self, interaction: discord.Interaction):
        """Show contribution information and GitHub repository link."""
        embed = discord.Embed(
            title="🤝 Contribute to SST Lounge Bot",
            description="**Help make the bot better for our SST Batch '29 community!**\n\n## 🎯 Your contributions matter",
            color=0x28a745
        )

        embed.add_field(
            name="🐛 Found a Bug?",
            value="**Report issues and help us improve**\n"
                  "```\n"
                  "Steps to Report:\n"
                  "1. Report it on GitHub Issues\n"
                  "2. Use our bug report template\n" 
                  "3. Include steps to reproduce\n"
                  "4. Mention the command that failed\n"
                  "```\n"
                  "[🔗 **Report Bug**](https://github.com/Muneer320/SST-Lounge-Bot/issues/new/choose)",
            inline=False
        )

        embed.add_field(
            name="💡 Have a Feature Idea?",
            value="**Suggest new features and enhancements**\n"
                  "```\n"
                  "How to Suggest:\n"
                  "1. Create a Feature Request\n"
                  "2. Use our feature request template\n"
                  "3. Explain how it helps our batch\n"
                  "4. Discuss implementation ideas\n"
                  "```\n"
                  "[🔗 **Suggest Feature**](https://github.com/Muneer320/SST-Lounge-Bot/issues/new/choose)",
            inline=False
        )

        embed.add_field(
            name="👨‍💻 Want to Code?",
            value="**Join our development team**\n"
                  "```\n"
                  "Development Process:\n"
                  "1. Fork the repository\n"
                  "2. Read CONTRIBUTING.md\n"
                  "3. Create a feature branch\n"
                  "4. Submit a Pull Request\n"
                  "```\n"
                  "[🔗 **Fork Repository**](https://github.com/Muneer320/SST-Lounge-Bot/fork)",
            inline=False
        )

        embed.add_field(
            name="🔗 Quick Links",
            value="### Important Resources:\n"
                  "🏠  [**Main Repository**](https://github.com/Muneer320/SST-Lounge-Bot)\n"
                  "📋  [**All Issues**](https://github.com/Muneer320/SST-Lounge-Bot/issues)\n"
                  "📖  [**Contributing Guide**](https://github.com/Muneer320/SST-Lounge-Bot/blob/main/.github/CONTRIBUTING.md)\n"
                  "📝  [**Create Issue**](https://github.com/Muneer320/SST-Lounge-Bot/issues/new/choose)",
            inline=False
        )

        embed.add_field(
            name="🌟 Areas We Need Help With",
            value="### Current Priorities:\n"
                  "• **Contest Features** → New platforms, better formatting\n"
                  "• **Utility Commands** → Batch coordination tools\n"
                  "• **Documentation** → Help guides, tutorials\n"
                  "• **Bug Fixes** → Performance optimizations\n"
                  "• **Testing** → Feature validation, edge cases",
            inline=False
        )

        embed.set_footer(
            text="Made by SST Batch '29 • For SST Batch '29 • Open Source ❤️ |"
        )
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the utility commands."""
    await bot.add_cog(UtilityCommands(bot))
