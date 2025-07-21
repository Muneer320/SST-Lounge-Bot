"""
Role Management Feature Module
Automatic role assignment based on Discord account age.
"""

import logging
import discord
from discord.ext import commands, tasks
from datetime import datetime
from typing import Optional
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.interaction_helpers import safe_response


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.VETERAN_ROLE_NAME = "Discord Veteran"
        self.VETERAN_THRESHOLD_YEARS = 5

        # Start background task
        self.veteran_role_check.start()

    async def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.veteran_role_check.cancel()

    @tasks.loop(hours=24)
    async def veteran_role_check(self):
        """
        Daily background task to check and assign Discord Veteran roles.

        Runs every 24 hours to:
        - Check all guild members for veteran qualification
        - Assign roles to newly qualified members
        - Log statistics and handle errors gracefully
        """
        try:
            self.logger.info("Starting daily Discord Veteran role check...")

            for guild in self.bot.guilds:
                await self.check_veteran_roles_in_guild(guild)

            self.logger.info("Completed daily Discord Veteran role check")

        except Exception as e:
            self.logger.error(f"Error in veteran_role_check: {e}")

    @veteran_role_check.before_loop
    async def before_veteran_check(self):
        """Wait for bot to be ready before starting the loop."""
        await self.bot.wait_until_ready()

    async def check_veteran_roles_in_guild(self, guild: discord.Guild):
        """
        Check and assign veteran roles for all members in a specific guild.

        Args:
            guild: The Discord guild to process

        Process:
        1. Get or create the Discord Veteran role
        2. Iterate through all non-bot members
        3. Check account age and assign role if qualified
        4. Apply rate limiting to avoid API issues
        """
        try:
            # Get or create the Discord Veteran role
            veteran_role = await self.get_or_create_veteran_role(guild)
            if not veteran_role:
                self.logger.warning(
                    f"Could not create Discord Veteran role in {guild.name}")
                return

            veteran_count = 0
            checked_count = 0

            # Check all members in the guild
            async for member in guild.fetch_members(limit=None):
                if member.bot:  # Skip bots
                    continue

                checked_count += 1

                # Check if member qualifies for veteran role
                if await self.is_discord_veteran(member):
                    if veteran_role not in member.roles:
                        try:
                            await member.add_roles(
                                veteran_role,
                                reason="Automatic: Discord account > 5 years old"
                            )
                            veteran_count += 1
                            self.logger.info(
                                f"Assigned Discord Veteran role to {member} in {guild.name}")

                            # Rate limiting: Small delay to avoid API limits
                            await asyncio.sleep(1)

                        except discord.Forbidden:
                            self.logger.warning(
                                f"No permission to assign role to {member} in {guild.name}")
                        except discord.HTTPException as e:
                            self.logger.error(
                                f"Failed to assign role to {member}: {e}")

            self.logger.info(
                f"Guild {guild.name}: Checked {checked_count} members, "
                f"assigned veteran role to {veteran_count} new members"
            )

        except Exception as e:
            self.logger.error(
                f"Error checking veteran roles in {guild.name}: {e}")

    async def get_or_create_veteran_role(self, guild: discord.Guild) -> Optional[discord.Role]:
        """Get existing Discord Veteran role or create it if it doesn't exist."""
        try:
            # Check if role already exists
            for role in guild.roles:
                if role.name == self.VETERAN_ROLE_NAME:
                    return role

            # Create the role if it doesn't exist
            veteran_role = await guild.create_role(
                name=self.VETERAN_ROLE_NAME,
                color=discord.Color.gold(),
                reason="Automatic role for Discord veterans (5+ years)",
                mentionable=True
            )

            self.logger.info(f"Created Discord Veteran role in {guild.name}")
            return veteran_role

        except discord.Forbidden:
            self.logger.error(f"No permission to create roles in {guild.name}")
            return None
        except discord.HTTPException as e:
            self.logger.error(
                f"Failed to create Discord Veteran role in {guild.name}: {e}")
            return None

    async def is_discord_veteran(self, member: discord.Member) -> bool:
        """Check if a member qualifies as a Discord veteran (5+ years)."""
        try:
            # Calculate account age
            account_age = datetime.utcnow() - member.created_at.replace(tzinfo=None)
            years = account_age.days / 365.25

            return years >= self.VETERAN_THRESHOLD_YEARS

        except Exception as e:
            self.logger.error(
                f"Error checking veteran status for {member}: {e}")
            return False

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Check new members for veteran status when they join."""
        try:
            if member.bot:  # Skip bots
                return

            if await self.is_discord_veteran(member):
                # Small delay to ensure member is fully loaded
                await asyncio.sleep(2)

                veteran_role = await self.get_or_create_veteran_role(member.guild)
                if veteran_role:
                    try:
                        await member.add_roles(veteran_role, reason="Automatic: New member is Discord veteran")
                        self.logger.info(
                            f"Assigned Discord Veteran role to new member {member}")
                    except discord.Forbidden:
                        self.logger.warning(
                            f"No permission to assign veteran role to new member {member}")
                    except discord.HTTPException as e:
                        self.logger.error(
                            f"Failed to assign veteran role to new member {member}: {e}")

        except Exception as e:
            self.logger.error(f"Error in on_member_join for {member}: {e}")

    @discord.app_commands.command(name="check_veterans", description="[Admin] Manually check and assign Discord Veteran roles")
    async def check_veterans_command(self, interaction: discord.Interaction):
        """Manual command to check and assign veteran roles."""
        try:
            # Check if command is used in a guild and user has admin permissions
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return

            if not isinstance(interaction.user, discord.Member):
                await interaction.response.send_message(
                    "❌ Unable to verify permissions.",
                    ephemeral=True
                )
                return

            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You need administrator permissions to use this command.",
                    ephemeral=True
                )
                return

            await interaction.response.defer(ephemeral=True)

            # Run the veteran check for this guild
            await self.check_veteran_roles_in_guild(interaction.guild)

            await interaction.followup.send("✅ Discord Veteran role check completed!")

        except Exception as e:
            self.logger.error(f"Error in check_veterans_command: {e}")
            await interaction.followup.send("❌ An error occurred while checking veteran roles.")

    @discord.app_commands.command(name="veteran_info", description="Show information about Discord Veteran role criteria")
    async def veteran_info_command(self, interaction: discord.Interaction):
        """Show information about the Discord Veteran role."""
        try:
            embed = discord.Embed(
                title="🥇 Discord Veteran Role",
                description="Automatic role for long-time Discord users",
                color=discord.Color.gold()
            )

            embed.add_field(
                name="📅 Qualification",
                value=f"Discord account must be **{self.VETERAN_THRESHOLD_YEARS}+ years old**",
                inline=False
            )

            embed.add_field(
                name="🤖 Assignment",
                value="• Automatically assigned when joining the server\n• Daily checks for existing members\n• Manual check available for admins",
                inline=False
            )

            embed.add_field(
                name="🎨 Role Details",
                value="• Color: Gold\n• Mentionable: Yes\n• Special recognition for Discord veterans",
                inline=False
            )

            # Check if user qualifies (only if in a guild)
            if interaction.guild and isinstance(interaction.user, discord.Member):
                if await self.is_discord_veteran(interaction.user):
                    account_age = datetime.utcnow() - interaction.user.created_at.replace(tzinfo=None)
                    years = account_age.days / 365.25
                    embed.add_field(
                        name="✅ Your Status",
                        value=f"You qualify! Your account is **{years:.1f} years old**",
                        inline=False
                    )
                else:
                    account_age = datetime.utcnow() - interaction.user.created_at.replace(tzinfo=None)
                    years = account_age.days / 365.25
                    years_needed = self.VETERAN_THRESHOLD_YEARS - years
                    embed.add_field(
                        name="⏳ Your Status",
                        value=f"Your account is **{years:.1f} years old**\nNeed **{years_needed:.1f} more years** to qualify",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="ℹ️ Note",
                    value="Use this command in a server to see your qualification status",
                    inline=False
                )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in veteran_info_command: {e}")
            await safe_response(interaction, "❌ An error occurred while fetching veteran information.")


async def setup(bot):
    await bot.add_cog(RoleManager(bot))
