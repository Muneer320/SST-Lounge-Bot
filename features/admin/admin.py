"""
Admin Feature Module
Administrative commands for SST Lounge Discord Server.
"""

import logging
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


def is_admin(interaction: discord.Interaction) -> bool:
    """Check if user has admin privileges."""
    if not interaction.guild:
        return False

    # Server owner always has admin privileges
    if interaction.user.id == interaction.guild.owner_id:
        logging.info(
            f"User {interaction.user} is server owner - granting admin access")
        return True

    # Check if user is a member and has administrator permission
    member = interaction.guild.get_member(interaction.user.id)
    if member and member.guild_permissions.administrator:
        logging.info(
            f"User {interaction.user} has administrator permission")
        return True

    logging.info(f"User {interaction.user} denied admin access")
    return False


class AdminCommands(commands.Cog):
    """Administrative commands for SST Lounge."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='info', description='Show bot information and statistics')
    async def info(self, interaction: discord.Interaction):
        """Show bot information and statistics."""
        logging.info(
            f"Info command used by {interaction.user} in {interaction.guild}")

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
        if not is_admin(interaction):
            await interaction.response.send_message("❌ Administrator permission or server ownership required.", ephemeral=True)
            return

        logging.info(f"Sync command used by {interaction.user}")
        await interaction.response.defer(ephemeral=True)

        try:
            synced = await self.bot.tree.sync()
            logging.info(f"Successfully synced {len(synced)} commands")

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

    @app_commands.command(name='grant_admin', description='Grant admin privileges to a user or role')
    @app_commands.describe(
        user='User to grant admin privileges to',
        role='Role to grant admin privileges to'
    )
    async def grant_admin(self, interaction: discord.Interaction, user: Optional[discord.Member] = None, role: Optional[discord.Role] = None):
        """Grant admin privileges to a user or role."""
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        # Only server owner can grant admin privileges
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Only the server owner can grant admin privileges.", ephemeral=True)
            return

        if not user and not role:
            await interaction.response.send_message("❌ Please specify either a user or role to grant admin privileges to.", ephemeral=True)
            return

        if user and role:
            await interaction.response.send_message("❌ Please specify either a user OR role, not both.", ephemeral=True)
            return

        try:
            # Check if bot has required permissions first
            bot_permissions = interaction.guild.me.guild_permissions
            if not bot_permissions.manage_roles:
                await interaction.response.send_message(
                    "❌ I couldn't do that. This could be due to:\n"
                    "• Bot's role is lower than the target role in the server hierarchy\n"
                    "• Bot wasn't invited with Administrator permission\n"
                    "• Server has unusual permission restrictions\n\n"
                    "Please ensure the bot has Administrator permission and its role is positioned high enough.",
                    ephemeral=True
                )
                return

            embed = None
            if user:
                # Grant administrator permission to user by updating their roles
                admin_role = discord.utils.get(
                    interaction.guild.roles, permissions=discord.Permissions(administrator=True))
                if not admin_role:
                    # Create admin role if it doesn't exist
                    admin_role = await interaction.guild.create_role(
                        name="SST Admin",
                        permissions=discord.Permissions(administrator=True),
                        color=discord.Color.red()
                    )
                    logging.info(f"Created new admin role: {admin_role.name}")

                await user.add_roles(admin_role)
                logging.info(f"Granted admin privileges to user {user}")

                embed = discord.Embed(
                    title="✅ Admin Privileges Granted",
                    description=f"Successfully granted administrator privileges to {user.mention}",
                    color=0x27ae60
                )

            elif role:
                # Update role permissions to include administrator
                await role.edit(permissions=discord.Permissions(administrator=True))
                logging.info(f"Granted admin privileges to role {role}")

                embed = discord.Embed(
                    title="✅ Admin Privileges Granted",
                    description=f"Successfully granted administrator privileges to role {role.mention}",
                    color=0x27ae60
                )

            if embed:
                await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to manage roles or permissions.", ephemeral=True)
        except Exception as e:
            logging.error(f"Error granting admin privileges: {e}")
            await interaction.response.send_message(f"❌ Failed to grant admin privileges: {str(e)}", ephemeral=True)

    @app_commands.command(name='revoke_admin', description='Revoke admin privileges from a user or role')
    @app_commands.describe(
        user='User to revoke admin privileges from',
        role='Role to revoke admin privileges from'
    )
    async def revoke_admin(self, interaction: discord.Interaction, user: Optional[discord.Member] = None, role: Optional[discord.Role] = None):
        """Revoke admin privileges from a user or role."""
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        # Only server owner can revoke admin privileges
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Only the server owner can revoke admin privileges.", ephemeral=True)
            return

        # Check if bot has permission to manage roles
        bot_permissions = interaction.guild.me.guild_permissions
        if not bot_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ I don't have permission to manage roles. Please ask a server admin to:\n"
                "1. Go to the Discord Developer Portal\n"
                "2. Update the bot's OAuth2 permissions to include 'Manage Roles'\n"
                "3. Re-invite the bot with the updated permissions",
                ephemeral=True
            )
            return

        if not user and not role:
            await interaction.response.send_message("❌ Please specify either a user or role to revoke admin privileges from.", ephemeral=True)
            return

        if user and role:
            await interaction.response.send_message("❌ Please specify either a user OR role, not both.", ephemeral=True)
            return

        try:
            embed = None
            if user:
                # Remove admin roles from user
                admin_roles = [
                    r for r in user.roles if r.permissions.administrator]
                if admin_roles:
                    await user.remove_roles(*admin_roles)
                    logging.info(f"Revoked admin privileges from user {user}")
                    embed = discord.Embed(
                        title="✅ Admin Privileges Revoked",
                        description=f"Successfully revoked administrator privileges from {user.mention}",
                        color=0x27ae60
                    )
                else:
                    embed = discord.Embed(
                        title="ℹ️ No Admin Privileges",
                        description=f"{user.mention} doesn't have administrator privileges to revoke.",
                        color=0x3498db
                    )

            elif role:
                # Remove administrator permission from role
                new_permissions = role.permissions
                new_permissions.administrator = False
                await role.edit(permissions=new_permissions)
                logging.info(f"Revoked admin privileges from role {role}")

                embed = discord.Embed(
                    title="✅ Admin Privileges Revoked",
                    description=f"Successfully revoked administrator privileges from role {role.mention}",
                    color=0x27ae60
                )

            if embed:
                await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to manage roles or permissions.", ephemeral=True)
        except Exception as e:
            logging.error(f"Error revoking admin privileges: {e}")
            await interaction.response.send_message(f"❌ Failed to revoke admin privileges: {str(e)}", ephemeral=True)


async def setup(bot):
    """Load the admin feature."""
    await bot.add_cog(AdminCommands(bot))
