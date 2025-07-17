"""
Admin Feature Module
Administrative commands for SST Lounge Discord Server.
"""

import logging
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List
import asyncio
from datetime import datetime, timedelta


# Autocomplete function for schedule parameter
async def schedule_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    now = datetime.now()
    options = [
        ("Now", "now"),
        ("In 1 hour", (now + timedelta(hours=1)).strftime("%H:%M")),
        ("Tonight", "23:00"),
        ("Midnight", "00:00"),
        ("Tomorrow morning", "08:00"),
    ]
    
    return [
        app_commands.Choice(name=label, value=value)
        for label, value in options if current.lower() in label.lower() or current.lower() in value.lower()
    ]


def is_admin(interaction: discord.Interaction) -> bool:
    """Check if user has admin privileges (server owner, Discord admin, or bot admin)."""
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
        logging.info(f"User {interaction.user} has administrator permission")
        return True

    # Note: Bot admin check will be done asynchronously in commands
    logging.info(f"User {interaction.user} requires bot admin check")
    return False


async def is_bot_admin(interaction: discord.Interaction, bot) -> bool:
    """Check if user has bot admin privileges (async version)."""
    if not interaction.guild:
        return False

    # Server owner always has admin privileges
    if interaction.user.id == interaction.guild.owner_id:
        return True

    # Check if user has Discord administrator permission
    if isinstance(interaction.user, discord.Member) and interaction.user.guild_permissions.administrator:
        return True

    # Check bot-level admin privileges
    if isinstance(interaction.user, discord.Member):
        # Check if user has direct bot admin privileges
        if await bot.db.is_bot_admin(interaction.guild.id, interaction.user.id, None):
            return True

        # Check if any of user's roles have bot admin privileges
        for role in interaction.user.roles:
            if await bot.db.is_bot_admin(interaction.guild.id, None, role.id):
                return True

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

        embed.add_field(
            name="🔗 Links",
            value="• **GitHub**: https://github.com/Muneer320/SST-Lounge-Bot\n"
                  "• **Contribute**: Use `/contribute` command\n"
                  "• **Support**: SST Batch '29 Discord Server",
            inline=False
        )

        embed.set_footer(
            text=f"Made for SST Batch '29 • Bot ID: {self.bot.user.id}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='sync', description='Sync slash commands')
    async def sync_commands(self, interaction: discord.Interaction):
        """Sync slash commands."""
        if not await is_bot_admin(interaction, self.bot):
            await interaction.response.send_message("❌ Administrator permission, server ownership, or bot admin privileges required.", ephemeral=True)
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

    @app_commands.command(name='grant_admin', description='Grant bot admin privileges to a user or role')
    @app_commands.describe(
        user='User to grant bot admin privileges to',
        role='Role to grant bot admin privileges to'
    )
    async def grant_admin(self, interaction: discord.Interaction, user: Optional[discord.Member] = None, role: Optional[discord.Role] = None):
        """Grant bot admin privileges to a user or role."""
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        # Only server owner can grant bot admin privileges
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Only the server owner can grant bot admin privileges.", ephemeral=True)
            return

        if not user and not role:
            await interaction.response.send_message("❌ Please specify either a user or role to grant bot admin privileges to.", ephemeral=True)
            return

        if user and role:
            await interaction.response.send_message("❌ Please specify either a user OR role, not both.", ephemeral=True)
            return

        try:
            embed = None
            if user:
                # Check if user already has bot admin privileges
                if await self.bot.db.is_bot_admin(interaction.guild.id, user.id, None):
                    embed = discord.Embed(
                        title="ℹ️ Already Bot Admin",
                        description=f"{user.mention} already has bot admin privileges.",
                        color=0x3498db
                    )
                else:
                    # Grant bot admin privileges to user
                    await self.bot.db.grant_bot_admin(interaction.guild.id, user.id, None, interaction.user.id)
                    logging.info(
                        f"Granted bot admin privileges to user {user}")

                    embed = discord.Embed(
                        title="✅ Bot Admin Privileges Granted",
                        description=f"Successfully granted bot admin privileges to {user.mention}",
                        color=0x27ae60
                    )

            elif role:
                # Check if role already has bot admin privileges
                if await self.bot.db.is_bot_admin(interaction.guild.id, None, role.id):
                    embed = discord.Embed(
                        title="ℹ️ Already Bot Admin",
                        description=f"Role {role.mention} already has bot admin privileges.",
                        color=0x3498db
                    )
                else:
                    # Grant bot admin privileges to role
                    await self.bot.db.grant_bot_admin(interaction.guild.id, None, role.id, interaction.user.id)
                    logging.info(
                        f"Granted bot admin privileges to role {role}")

                    embed = discord.Embed(
                        title="✅ Bot Admin Privileges Granted",
                        description=f"Successfully granted bot admin privileges to role {role.mention}",
                        color=0x27ae60
                    )

            if embed:
                embed.add_field(
                    name="Note",
                    value="These are bot-level admin privileges, not Discord server permissions.",
                    inline=False
                )
                await interaction.response.send_message(embed=embed)

        except Exception as e:
            logging.error(f"Error granting bot admin privileges: {e}")
            await interaction.response.send_message(f"❌ Failed to grant bot admin privileges: {str(e)}", ephemeral=True)

    @app_commands.command(name='revoke_admin', description='Revoke bot admin privileges from a user or role')
    @app_commands.describe(
        user='User to revoke bot admin privileges from',
        role='Role to revoke bot admin privileges from'
    )
    async def revoke_admin(self, interaction: discord.Interaction, user: Optional[discord.Member] = None, role: Optional[discord.Role] = None):
        """Revoke bot admin privileges from a user or role."""
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        # Only server owner can revoke bot admin privileges
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Only the server owner can revoke bot admin privileges.", ephemeral=True)
            return

        if not user and not role:
            await interaction.response.send_message("❌ Please specify either a user or role to revoke bot admin privileges from.", ephemeral=True)
            return

        if user and role:
            await interaction.response.send_message("❌ Please specify either a user OR role, not both.", ephemeral=True)
            return

        try:
            embed = None
            if user:
                # Check if user has bot admin privileges
                if not await self.bot.db.is_bot_admin(interaction.guild.id, user.id, None):
                    embed = discord.Embed(
                        title="ℹ️ No Bot Admin Privileges",
                        description=f"{user.mention} doesn't have bot admin privileges to revoke.",
                        color=0x3498db
                    )
                else:
                    # Revoke bot admin privileges from user
                    await self.bot.db.revoke_bot_admin(interaction.guild.id, user.id, None)
                    logging.info(
                        f"Revoked bot admin privileges from user {user}")

                    embed = discord.Embed(
                        title="✅ Bot Admin Privileges Revoked",
                        description=f"Successfully revoked bot admin privileges from {user.mention}",
                        color=0x27ae60
                    )

            elif role:
                # Check if role has bot admin privileges
                if not await self.bot.db.is_bot_admin(interaction.guild.id, None, role.id):
                    embed = discord.Embed(
                        title="ℹ️ No Bot Admin Privileges",
                        description=f"Role {role.mention} doesn't have bot admin privileges to revoke.",
                        color=0x3498db
                    )
                else:
                    # Revoke bot admin privileges from role
                    await self.bot.db.revoke_bot_admin(interaction.guild.id, None, role.id)
                    logging.info(
                        f"Revoked bot admin privileges from role {role}")

                    embed = discord.Embed(
                        title="✅ Bot Admin Privileges Revoked",
                        description=f"Successfully revoked bot admin privileges from role {role.mention}",
                        color=0x27ae60
                    )

            if embed:
                await interaction.response.send_message(embed=embed)

        except Exception as e:
            logging.error(f"Error revoking bot admin privileges: {e}")
            await interaction.response.send_message(f"❌ Failed to revoke bot admin privileges: {str(e)}", ephemeral=True)

    @app_commands.command(name='list_admins', description='List all bot admin users and roles')
    async def list_admins(self, interaction: discord.Interaction):
        """List all bot admin users and roles."""
        # Check if command is used in a guild
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers.", ephemeral=True)
            return

        # Only server owner or bot admins can view admin list
        if not await is_bot_admin(interaction, self.bot):
            await interaction.response.send_message("❌ Administrator permission, server ownership, or bot admin privileges required.", ephemeral=True)
            return

        try:
            admins = await self.bot.db.get_bot_admins(interaction.guild.id)

            embed = discord.Embed(
                title="🛡️ Bot Admin List",
                color=0x3498db
            )

            if not admins:
                embed.description = "No bot admins have been granted privileges yet."
            else:
                user_admins = []
                role_admins = []

                for admin in admins:
                    if admin['user_id']:
                        user = interaction.guild.get_member(admin['user_id'])
                        if user:
                            granted_by = interaction.guild.get_member(
                                admin['granted_by'])
                            granted_by_name = granted_by.display_name if granted_by else "Unknown"
                            user_admins.append(
                                f"• {user.mention} (granted by {granted_by_name})")
                        else:
                            user_admins.append(
                                f"• <@{admin['user_id']}> (user left server)")

                    elif admin['role_id']:
                        role = interaction.guild.get_role(admin['role_id'])
                        if role:
                            granted_by = interaction.guild.get_member(
                                admin['granted_by'])
                            granted_by_name = granted_by.display_name if granted_by else "Unknown"
                            role_admins.append(
                                f"• {role.mention} (granted by {granted_by_name})")
                        else:
                            role_admins.append(
                                f"• Role ID {admin['role_id']} (role deleted)")

                if user_admins:
                    embed.add_field(
                        name=f"👤 User Admins ({len(user_admins)})",
                        value="\n".join(
                            user_admins[:10]) + ("..." if len(user_admins) > 10 else ""),
                        inline=False
                    )

                if role_admins:
                    embed.add_field(
                        name=f"🎭 Role Admins ({len(role_admins)})",
                        value="\n".join(
                            role_admins[:10]) + ("..." if len(role_admins) > 10 else ""),
                        inline=False
                    )

                embed.add_field(
                    name="Default Admins",
                    value=f"• Server Owner: <@{interaction.guild.owner_id}>\n• Discord Administrators (automatic)",
                    inline=False
                )

            embed.set_footer(
                text="Bot admins have access to administrative commands but not Discord server permissions")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logging.error(f"Error listing bot admins: {e}")
            await interaction.response.send_message(f"❌ Failed to list bot admins: {str(e)}", ephemeral=True)

    @app_commands.command(name='update', description='Update the bot to the latest version')
    @app_commands.describe(
        schedule='Schedule the update for a specific time (default: now)'
    )
    @app_commands.autocomplete(schedule=schedule_autocomplete)
    async def update_bot(self, interaction: discord.Interaction, schedule: Optional[str] = "now"):
        """Update the bot to the latest version from GitHub."""
        # Check if user has bot admin privileges
        if not await is_bot_admin(interaction, self.bot):
            await interaction.response.send_message("❌ Administrator permission, server ownership, or bot admin privileges required.", ephemeral=True)
            return

        logging.info(f"Update command used by {interaction.user} with schedule: {schedule}")

        try:
            # Check if update is available
            update_available, version_info = await self.bot.updater.check_for_updates()
            
            if not update_available:
                await interaction.response.send_message("✅ Bot is already at the latest version.", ephemeral=True)
                return
            
            # Get version info
            current_version = self.bot.updater.current_version.get('version', 'unknown')
            new_version = version_info.get('version', 'unknown') if version_info else 'unknown'
            description = version_info.get('description', 'No description available') if version_info else 'No description available'
            
            # Handle scheduled updates
            scheduled_time = None
            if schedule and schedule.lower() != "now":
                try:
                    # Parse the time
                    hour, minute = map(int, schedule.split(':'))
                    now = datetime.now()
                    scheduled_time = now.replace(hour=hour, minute=minute)
                    
                    # If the time is in the past, schedule for tomorrow
                    if scheduled_time < now:
                        scheduled_time = scheduled_time + timedelta(days=1)
                        
                    time_diff = scheduled_time - now
                    hours, remainder = divmod(time_diff.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    
                    schedule_text = f"scheduled for {scheduled_time.strftime('%H:%M')} (in {hours}h {minutes}m)"
                except ValueError:
                    await interaction.response.send_message("❌ Invalid time format. Use HH:MM format or select from autocomplete options.", ephemeral=True)
                    return
            else:
                schedule_text = "now"
            
            # Confirm the update
            embed = discord.Embed(
                title="🔄 Update Available",
                description=f"Are you sure you want to update the bot from v{current_version} to v{new_version} {schedule_text}?",
                color=0x3498db
            )
            embed.add_field(name="Description", value=description, inline=False)
            embed.add_field(name="Warning", value="Bot will restart during the update process.", inline=False)
            
            # Create confirmation buttons
            class ConfirmView(discord.ui.View):
                def __init__(self, *, timeout=180, bot=None, scheduled_time=None):
                    super().__init__(timeout=timeout)
                    self.bot = bot
                    self.scheduled_time = scheduled_time
                
                @discord.ui.button(label="Update Now", style=discord.ButtonStyle.green)
                async def confirm_callback(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    if button_interaction.user.id != interaction.user.id:
                        await button_interaction.response.send_message("❌ Only the command user can confirm.", ephemeral=True)
                        return
                    
                    # Create a new view with disabled buttons
                    disabled_view = discord.ui.View()
                    disabled_view.add_item(discord.ui.Button(label="Update Now", style=discord.ButtonStyle.green, disabled=True))
                    disabled_view.add_item(discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red, disabled=True))
                    
                    # Process based on scheduling
                    if self.scheduled_time:
                        time_diff = self.scheduled_time - datetime.now()
                        wait_seconds = time_diff.total_seconds()
                        
                        if wait_seconds <= 0:
                            # Scheduled time is now or in the past
                            await button_interaction.response.edit_message(content="🔄 Starting update process immediately...", view=disabled_view)
                            if self.bot is not None:
                                await self.bot.updater.update(button_interaction)
                        else:
                            # Schedule for future time
                            hours, remainder = divmod(int(wait_seconds), 3600)
                            minutes, seconds = divmod(remainder, 60)
                            schedule_message = f"✅ Update scheduled for {self.scheduled_time.strftime('%H:%M')} (in {hours}h {minutes}m)"
                            
                            await button_interaction.response.edit_message(content=schedule_message, embed=None, view=disabled_view)
                            
                            # Create a background task to perform the update at the scheduled time
                            async def scheduled_update():
                                await asyncio.sleep(wait_seconds)
                                try:
                                    # Send a notification that the scheduled update is starting
                                    await button_interaction.followup.send("🔄 Scheduled update starting now...", ephemeral=True)
                                    if self.bot is not None:
                                        await self.bot.updater.update(None)
                                except Exception as e:
                                    logging.error(f"Error in scheduled update: {e}")
                            
                            # Start the background task
                            asyncio.create_task(scheduled_update())
                    else:
                        # Immediate update
                        await button_interaction.response.edit_message(content="🔄 Starting update process...", view=disabled_view)
                        if self.bot is not None:
                            await self.bot.updater.update(button_interaction)
                        else:
                            await button_interaction.followup.send("Bot reference is missing. Update failed.", ephemeral=True)
                
                @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
                async def cancel_callback(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    if button_interaction.user.id != interaction.user.id:
                        await button_interaction.response.send_message("❌ Only the command user can cancel.", ephemeral=True)
                        return
                    
                    # Create a new view with disabled buttons
                    disabled_view = discord.ui.View()
                    disabled_view.add_item(discord.ui.Button(label="Update Now", style=discord.ButtonStyle.green, disabled=True))
                    disabled_view.add_item(discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red, disabled=True))
                    
                    await button_interaction.response.edit_message(content="Update cancelled.", embed=None, view=disabled_view)
            
            # Send confirmation message with buttons
            view = ConfirmView(bot=self.bot, scheduled_time=scheduled_time)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Error in update command: {e}")
            await interaction.response.send_message(f"❌ Error checking for updates: {str(e)}", ephemeral=True)


async def setup(bot):
    """Load the admin feature."""
    await bot.add_cog(AdminCommands(bot))
