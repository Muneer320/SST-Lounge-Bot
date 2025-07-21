"""
Interaction Helper Utilities

Centralized utilities for safe Discord interaction handling to prevent common
interaction acknowledgment errors. This module provides robust wrapper functions
that handle edge cases where interactions may already be acknowledged.

Key Functions:
- safe_response(): Send responses with automatic fallback to followup
- safe_defer(): Safely defer interactions with acknowledgment checking

These utilities prevent the common "Interaction has already been acknowledged" 
errors that can occur in complex command flows.
"""

import discord
import logging

logger = logging.getLogger(__name__)

async def safe_response(interaction: discord.Interaction, *args, **kwargs):
    """
    Safely send a response, using followup if already acknowledged.
    
    This function handles cases where an interaction has already been responded to,
    preventing "Interaction has already been acknowledged" errors.
    
    Args:
        interaction: Discord interaction object
        *args: Arguments to pass to send_message
        **kwargs: Keyword arguments to pass to send_message
    """
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(*args, **kwargs)
        else:
            await interaction.followup.send(*args, **kwargs)
    except discord.HTTPException as e:
        logger.warning(f"Failed to send response normally, trying followup: {e}")
        try:
            await interaction.followup.send(*args, **kwargs)
        except discord.HTTPException as e2:
            logger.error(f"Failed to send followup response: {e2}")

async def safe_defer(interaction: discord.Interaction, ephemeral: bool = False):
    """
    Safely defer an interaction, handling cases where it's already acknowledged.
    
    Args:
        interaction: Discord interaction object
        ephemeral: Whether the response should be ephemeral
        
    Returns:
        bool: True if defer was successful, False if already acknowledged
    """
    try:
        await interaction.response.defer(ephemeral=ephemeral)
        return True
    except discord.HTTPException:
        logger.debug("Interaction already acknowledged, cannot defer")
        return False
