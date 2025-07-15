"""
Admin Feature Module
Administrative commands for SST Lounge Discord Server.
"""

import logging
import discord
from discord.ext import commands
from discord import app_commands


class AdminCommands(commands.Cog):
    """Administrative commands for SST Lounge."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='info', description='Show bot information and statistics')
    async def info(self, interaction: discord.Interaction):
        """Show bot information and statistics."""
        # Check if user has admin permissions
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        member = interaction.guild.get_member(interaction.user.id)
        if not member or not member.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permission required.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🤖 SST Lounge Bot Info",
            description="Bot statistics and information",
            color=0x3498db
        )

        embed.add_field(
            name="📊 Server Stats",
            value=f"**Guilds:** {len(self.bot.guilds)}\n"
            f"**Users:** {len(self.bot.users)}\n"
            f"**Latency:** {round(self.bot.latency * 1000)}ms",
            inline=True
        )

        embed.add_field(
            name="🔧 Technical",
            value=f"**Discord.py:** {discord.__version__}\n"
            f"**Features:** {len(self.bot.cogs)}\n"
            f"**Commands:** Slash only",
            inline=True
        )

        # Show connected servers (for owner)
        if len(self.bot.guilds) <= 3:  # Only show if in few servers
            guild_list = []
            for guild in self.bot.guilds:
                guild_list.append(
                    f"• {guild.name} ({guild.member_count} members)")

            if guild_list:
                embed.add_field(
                    name="🏠 Connected Servers",
                    value="\n".join(guild_list),
                    inline=False
                )

        embed.set_footer(
            text=f"Made for SST Batch '29 • Bot ID: {self.bot.user.id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='sync', description='Sync slash commands')
    async def sync_commands(self, interaction: discord.Interaction):
        """Sync slash commands."""
        # Check if user has admin permissions
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        member = interaction.guild.get_member(interaction.user.id)
        if not member or not member.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permission required.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            synced = await self.bot.tree.sync()
            embed = discord.Embed(
                title="✅ Commands Synced",
                description=f"Successfully synced {len(synced)} slash commands.",
                color=0x27ae60
            )

            if synced:
                command_list = [f"• /{cmd.name}" for cmd in synced[:10]]
                embed.add_field(
                    name="Synced Commands",
                    value="\n".join(command_list) +
                    ("..." if len(synced) > 10 else ""),
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logging.error(f"Error syncing commands: {e}")
            embed = discord.Embed(
                title="❌ Sync Failed",
                description=f"Failed to sync commands: {str(e)}",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    """Load the admin feature."""
    await bot.add_cog(AdminCommands(bot))
