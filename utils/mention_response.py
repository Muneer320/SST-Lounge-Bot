"""
Mention Response Utilities
Handles bot mention responses with interactive UI components.
"""

import discord
import logging


class MentionResponseView(discord.ui.View):
    """Interactive buttons for mention responses."""

    def __init__(self):
        super().__init__(timeout=300)
        github_button = discord.ui.Button(
            label="Contribute",
            style=discord.ButtonStyle.link,
            url="https://github.com/Muneer320/SST-Lounge-Bot",
            emoji="🤝"
        )
        self.add_item(github_button)

    @discord.ui.button(label="Help & Commands", style=discord.ButtonStyle.primary, emoji="📋")
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show help information."""
        try:
            embed = discord.Embed(
                title="🤖 SST Lounge Bot - Quick Help",
                description="Here are the main command categories:",
                color=0x2ecc71
            )

            embed.add_field(
                name="🏆 Contest Commands",
                value="`/contests` - Upcoming contests\n"
                      "`/contests_today` - Today's contests\n"
                      "`/contests_tomorrow` - Tomorrow's contests",
                inline=True
            )

            embed.add_field(
                name="🛠️ Utility Commands",
                value="`/ping` - Check bot latency\n"
                      "`/hello` - Friendly greeting\n"
                      "`/help` - Complete command guide",
                inline=True
            )

            embed.add_field(
                name="🎭 Role Commands",
                value="`/veteran_info` - Role criteria\n"
                      "`/check_veterans` - Check roles (Admin)",
                inline=True
            )

            embed.add_field(
                name="💡 Pro Tips",
                value="• Use `/help` for the complete command guide\n"
                      "• All contest times are in IST timezone\n"
                      "• Admins have access to additional commands",
                inline=False
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            await interaction.response.send_message(
                "Use `/help` to see all available commands!", ephemeral=True
            )

    @discord.ui.button(label="View Contests", style=discord.ButtonStyle.secondary, emoji="🏆")
    async def contests_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Quick contest information."""
        try:
            embed = discord.Embed(
                title="🏆 Contest System",
                description="Get the latest programming contest information!",
                color=0xe74c3c
            )

            embed.add_field(
                name="📅 Available Commands",
                value="`/contests` - Next 3 days of contests\n"
                      "`/contests_today` - Today's contests with live status\n"
                      "`/contests_tomorrow` - Tomorrow's contests",
                inline=False
            )

            embed.add_field(
                name="🎯 Supported Platforms",
                value="🔵 **Codeforces** • 🟡 **CodeChef**\n"
                      "🟠 **AtCoder** • 🟢 **LeetCode**",
                inline=False
            )

            embed.add_field(
                name="✨ Features",
                value="• Real-time contest status (⏰ Upcoming, 🔴 Running, ✅ Ended)\n"
                      "• Platform filtering and result limits\n"
                      "• All times displayed in IST timezone\n"
                      "• Smart caching for instant responses",
                inline=False
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            await interaction.response.send_message(
                "Use `/contests` to see upcoming programming contests!", ephemeral=True
            )

    @discord.ui.button(label="Bot Stats", style=discord.ButtonStyle.secondary, emoji="📊")
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show bot statistics."""
        try:
            bot = interaction.client
            embed = discord.Embed(
                title="📊 Bot Statistics",
                color=0x9b59b6
            )

            embed.add_field(
                name="🌐 Server Info",
                value=f"**Servers:** {len(bot.guilds)}\n"
                f"**Latency:** {round(bot.latency * 1000)}ms",
                inline=True
            )

            embed.add_field(
                name="⚡ Performance",
                value="**Cache:** Active\n"
                      "**Status:** Operational\n"
                      "**Updates:** Auto-enabled",
                inline=True
            )

            embed.add_field(
                name="🛠️ Features Active",
                value="✅ Contest Tracking\n"
                      "✅ Role Management\n"
                      "✅ Admin System\n"
                      "✅ Auto Updates",
                inline=False
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            await interaction.response.send_message(
                "Bot is running smoothly! Use `/info` for detailed statistics.", ephemeral=True
            )


class MentionResponseHandler:
    """Handles bot mention responses and creates beautiful greeting messages."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('SSTLounge.MentionResponse')

    async def send_mention_response(self, message):
        """Send a beautiful greeting response when the bot is mentioned."""
        try:
            # Create main embed
            embed = discord.Embed(
                title="👋 Hey there, SST Batch '29!",
                description=f"Hello {message.author.mention}! I'm the **SST Lounge Bot** 🤖\n"
                f"Your friendly assistant for contest tracking, server management, and batch coordination!",
                color=0x3498db
            )

            # Add feature highlights
            embed.add_field(
                name="🏆 Contest Features",
                value="• Real-time contest tracking\n"
                      "• Daily contest announcements\n"
                      "• Platform filtering & status updates\n"
                      "• Supports Codeforces, CodeChef, AtCoder, LeetCode",
                inline=True
            )

            embed.add_field(
                name="🎭 Role Management",
                value="• Automatic Discord Veteran roles\n"
                      "• Member join detection\n"
                      "• Daily role checks\n"
                      "• Smart role creation",
                inline=True
            )

            embed.add_field(
                name="⚙️ Admin Tools",
                value="• Three-tier permission system\n"
                      "• Advanced logging & exports\n"
                      "• Auto-update system\n"
                      "• Comprehensive error handling",
                inline=True
            )

            # Add quick info
            embed.add_field(
                name="📊 Quick Stats",
                value=f"🌐 Serving **{len(self.bot.guilds)}** servers\n"
                f"⚡ Latency: **{round(self.bot.latency * 1000)}ms**\n"
                f"🕒 Uptime: Since last restart",
                inline=False
            )

            embed.set_footer(
                text="Made with ❤️ for SST Batch '29 • Use the buttons below for quick access!",
                icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
            )

            embed.set_thumbnail(
                url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None)

            # Create interactive buttons
            view = MentionResponseView()

            await message.channel.send(embed=embed, view=view)
            self.logger.info(
                f"Sent mention response to {message.author} in {message.guild}")

        except Exception as e:
            self.logger.error(f"Error sending mention response: {e}")
            # Simple fallback response
            try:
                await message.channel.send(
                    f"👋 Hello {message.author.mention}! I'm the SST Lounge Bot. "
                    f"Use `/help` to see all my commands!"
                )
            except Exception as fallback_error:
                self.logger.error(
                    f"Fallback mention response failed: {fallback_error}")
