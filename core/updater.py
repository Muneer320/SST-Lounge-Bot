"""Read-only release checks and once-per-version administrator notices."""

import asyncio
import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import aiohttp


logger = logging.getLogger("SSTLounge.Updater")


def version_parts(value):
    """Return a comparable three-part release version, or None."""
    if not isinstance(value, str):
        return None
    parts = value.split(".")
    if len(parts) != 3 or not all(part.isascii() and part.isdigit() for part in parts):
        return None
    return tuple(map(int, parts))


class GitUpdater:
    """Checks version.json without mutating a running bot process."""

    def __init__(self, bot, check_interval=600):
        self.bot = bot
        self.check_interval = max(60, int(check_interval))
        self.repo_url = os.getenv("GITHUB_REPO_URL", "https://github.com/Muneer320/SST-Lounge-Bot")
        self.branch = os.getenv("GITHUB_REPO_BRANCH", "main") or "main"
        parsed = urlparse(self.repo_url)
        segments = [segment for segment in parsed.path.strip("/").split("/") if segment]
        if parsed.hostname == "github.com" and len(segments) == 2:
            self.repo_owner, self.repo_name = segments
            self.repo_name = self.repo_name.removesuffix(".git")
        else:
            self.repo_owner = self.repo_name = None
        self.version_file = Path(__file__).resolve().parent.parent / "version.json"
        self.current_version = self._load_current_version()
        self.running = False

    def _load_current_version(self):
        try:
            return json.loads(self.version_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            logger.error("Cannot read local version.json: %s", exc)
            return {"version": "0.0.0"}

    async def check_for_updates(self):
        """Compare published version metadata; fail closed on bad responses."""
        if not self.repo_owner or not self.repo_name:
            logger.warning("Update check skipped: invalid GitHub repository URL")
            return False, None
        url = (
            f"https://raw.githubusercontent.com/{self.repo_owner}/"
            f"{self.repo_name}/{self.branch}/version.json"
        )
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    remote = await response.json(content_type=None)
            if not isinstance(remote, dict):
                logger.warning("Update check skipped: expected version metadata object")
                return False, None
            current = version_parts(self.current_version.get("version"))
            available = version_parts(remote.get("version"))
            if current is None or available is None:
                logger.warning("Update check skipped: invalid version metadata")
                return False, None
            return available > current, remote
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, TypeError) as exc:
            logger.warning("Update check failed: %s", exc)
            return False, None

    async def notify_update_available(self, version_info):
        """DM directly granted admins once per version across all guilds."""
        version = version_info.get("version")
        if version_parts(version) is None:
            return
        user_ids = set()
        for guild in self.bot.guilds:
            try:
                admins = await self.bot.db.get_bot_admins(guild.id)
                user_ids.update(admin["user_id"] for admin in admins if admin.get("user_id"))
            except Exception as exc:
                logger.warning("Cannot load admins for guild %s: %s", guild.id, exc)
        message = (
            f"A new SST Lounge Bot release is available: v{version}.\n"
            f"Current version: v{self.current_version.get('version', 'unknown')}\n"
            "Ask the host operator to redeploy from the updated repository. "
            "The bot does not replace its own running process."
        )
        for user_id in user_ids:
            if await self.bot.db.was_update_notified(user_id, version):
                continue
            try:
                user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                await user.send(message)
                await self.bot.db.mark_update_notified(user_id, version)
            except Exception as exc:
                logger.warning("Cannot notify admin %s: %s", user_id, exc)

    async def start_update_checker(self):
        self.running = True
        while self.running:
            try:
                available, version_info = await self.check_for_updates()
                if available:
                    await self.notify_update_available(version_info)
            except Exception:
                logger.exception("Update checker failed")
            await asyncio.sleep(self.check_interval)

    def stop(self):
        self.running = False
