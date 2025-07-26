"""
Interaction Helper Utilities
Safe Discord interaction handling to prevent acknowledgment errors.
"""

import discord
import logging

logger = logging.getLogger(__name__)


async def safe_response(interaction: discord.Interaction, *args, **kwargs):
    """Safely send a response, using followup if already acknowledged."""
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(*args, **kwargs)
        else:
            await interaction.followup.send(*args, **kwargs)
    except discord.HTTPException as e:
        logger.warning(
            f"Failed to send response normally, trying followup: {e}")
        try:
            await interaction.followup.send(*args, **kwargs)
        except discord.HTTPException as e2:
            logger.error(f"Failed to send followup response: {e2}")


async def safe_defer(interaction: discord.Interaction, ephemeral: bool = False):
    """Safely defer an interaction, handling cases where it's already acknowledged."""
    try:
        await interaction.response.defer(ephemeral=ephemeral)
        return True
    except discord.HTTPException:
        logger.debug("Interaction already acknowledged, cannot defer")
        return False
