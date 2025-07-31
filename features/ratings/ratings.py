"""Competitive programming ratings from the companion CPStats API."""

import os
import re
from urllib.parse import quote, urlparse

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


PLATFORMS = ("codeforces", "codechef", "atcoder", "leetcode")
HANDLE_PATTERN = re.compile(r"[A-Za-z0-9_.-]{1,32}\Z")


class RatingUnavailable(Exception):
    """A rating cannot be shown accurately."""


def rating_config():
    base_url = os.getenv("CPSTATS_API_URL", "").rstrip("/")
    api_key = os.getenv("CPSTATS_API_KEY", "")
    parsed = urlparse(base_url)
    local_http = parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1"}
    if not api_key or not parsed.netloc or not (parsed.scheme == "https" or local_http):
        raise RatingUnavailable("CPStats API is not configured. Ask the host operator to set its URL and key.")
    return base_url, api_key


async def fetch_rating(platform: str, username: str):
    if platform not in PLATFORMS or not HANDLE_PATTERN.fullmatch(username):
        raise RatingUnavailable("Choose a supported platform and a valid handle (1–32 characters).")
    base_url, api_key = rating_config()
    url = f"{base_url}/rating/{platform}/{quote(username, safe='')}"
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers={"Authorization": f"Bearer {api_key}"}) as response:
                if response.status != 200:
                    raise RatingUnavailable(f"CPStats API returned HTTP {response.status}.")
                result = await response.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
        raise RatingUnavailable("CPStats API is unavailable. Try again later.") from exc
    if not isinstance(result, dict):
        raise RatingUnavailable("CPStats API did not return a usable rating.")
    if result.get("status") != "success" or not isinstance(result.get("rating"), (int, float)):
        if result.get("status") == "user_not_found":
            raise RatingUnavailable(f"No {platform} profile was found for {username}.")
        raise RatingUnavailable("CPStats API did not return a usable rating.")
    return result


class RatingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cp_rating", description="Show a competitive programming rating")
    @app_commands.describe(platform="Rating platform", username="Public profile handle")
    @app_commands.choices(platform=[app_commands.Choice(name=name.title(), value=name) for name in PLATFORMS])
    async def cp_rating(self, interaction: discord.Interaction, platform: str, username: str):
        await interaction.response.defer()
        try:
            result = await fetch_rating(platform, username)
        except RatingUnavailable as exc:
            await interaction.followup.send(str(exc), ephemeral=True)
            return
        embed = discord.Embed(
            title=f"{platform.title()} rating: {username}",
            description=f"Current rating: **{result['rating']}**",
            color=0x3498DB,
        )
        if result.get("max_rating") is not None:
            embed.add_field(name="Peak rating", value=str(result["max_rating"]))
        if result.get("rank"):
            embed.add_field(name="Rank", value=str(result["rank"]))
        embed.set_footer(text="Data from CPStats API; ratings may be cached")
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RatingCommands(bot))
