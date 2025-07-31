"""Offline contract tests for the bot's local and external boundaries."""

import asyncio
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytz
from aiohttp import web

from core.database import SimpleDB
from core.bot import SSTLoungeBot
from core.updater import GitUpdater, version_parts
from features.contests.contests import ContestAPI
from features.ratings.ratings import RatingUnavailable, fetch_rating


IST = pytz.timezone("Asia/Kolkata")


def sample_contest(day_offset=0):
    start = (datetime.now(IST) + timedelta(days=day_offset)).replace(
        hour=18, minute=0, second=0, microsecond=0
    )
    return {
        "id": 41723 + day_offset,
        "event": "SST Practice Round",
        "resource": "codeforces.com",
        "start": start.astimezone(pytz.UTC).isoformat(),
        "duration": 7200,
        "href": "https://codeforces.com/contests",
    }


class VersionTests(unittest.TestCase):
    def test_numeric_release_order_and_invalid_values(self):
        self.assertGreater(version_parts("1.10.0"), version_parts("1.9.9"))
        for value in ("1.2", "1.2.beta", "1.2.3-dev", None):
            self.assertIsNone(version_parts(value))

    def test_clist_id_is_stable(self):
        api = ContestAPI()
        record = sample_contest()
        self.assertEqual(api._process_contests([record])[0]["id"], str(record["id"]))


class ReleaseCheckTests(unittest.IsolatedAsyncioTestCase):
    async def test_remote_version_is_compared_numerically(self):
        class Response:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return None

            def raise_for_status(self):
                return None

            async def json(self, content_type=None):
                return {"version": "1.10.0"}

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return None

            def get(self, url):
                self_url = "https://raw.githubusercontent.com/Muneer320/SST-Lounge-Bot/main/version.json"
                assert url == self_url
                return Response()

        updater = GitUpdater(SimpleNamespace())
        updater.current_version = {"version": "1.9.9"}
        with patch("core.updater.aiohttp.ClientSession", return_value=Session()):
            available, remote = await updater.check_for_updates()
        self.assertTrue(available)
        self.assertEqual(remote["version"], "1.10.0")


class DatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tempdir.name) / "nested" / "bot.db")
        self.db = SimpleDB(self.db_path)
        await self.db.initialize()

    async def asyncTearDown(self):
        await self.db.close()
        self.tempdir.cleanup()

    async def test_settings_keep_channel_and_time(self):
        await self.db.set_announcement_time(10, "08:30")
        await self.db.set_contest_channel(10, 99)
        self.assertEqual(await self.db.get_announcement_time(10), "08:30")
        self.assertEqual(await self.db.get_contest_channel(10), 99)
        await self.db.set_announcement_time(10, "09:00")
        self.assertEqual(await self.db.get_contest_channel(10), 99)
        self.assertTrue(await self.db.should_send_announcement(10))
        await self.db.mark_announcement_sent(10)
        self.assertFalse(await self.db.should_send_announcement(10))

    async def test_cache_round_trip_uses_stable_id_and_ist_day(self):
        processed = ContestAPI()._process_contests([sample_contest(), sample_contest(1)])
        api = SimpleNamespace(fetch_upcoming_contests=lambda days: asyncio.sleep(0, result=processed))
        self.assertEqual(await self.db.fetch_and_cache_contests(api), 2)
        self.assertFalse(await self.db.is_cache_stale())
        today = await self.db.get_contests_today()
        tomorrow = await self.db.get_contests_tomorrow()
        self.assertEqual([item["id"] for item in today], ["41723"])
        self.assertEqual([item["id"] for item in tomorrow], ["41724"])
        await self.db.close()
        self.db = SimpleDB(self.db_path)
        await self.db.initialize()
        self.assertEqual(len(await self.db.get_cached_contests()), 2)

    async def test_notices_are_once_per_user_and_version(self):
        await self.db.grant_bot_admin(10, user_id=7, granted_by=1)
        await self.db.grant_bot_admin(10, role_id=99, granted_by=1)
        sent = []

        class User:
            async def send(self, message):
                sent.append(message)

        bot = SimpleNamespace(
            db=self.db,
            guilds=[SimpleNamespace(id=10), SimpleNamespace(id=10)],
            get_user=lambda user_id: User(),
        )
        updater = GitUpdater(bot)
        await updater.notify_update_available({"version": "1.6.0"})
        await updater.notify_update_available({"version": "1.6.0"})
        self.assertEqual(len(sent), 1)
        await updater.notify_update_available({"version": "1.6.1"})
        self.assertEqual(len(sent), 2)
        self.assertTrue(await self.db.was_update_notified(7, "1.6.1"))


class RatingTests(unittest.IsolatedAsyncioTestCase):
    async def test_local_companion_api_and_error_status(self):
        async def rating(request):
            self.assertEqual(request.headers.get("Authorization"), "Bearer demo-key")
            if request.match_info["username"] == "missing":
                return web.json_response({"status": "user_not_found", "rating": 0})
            return web.json_response({"status": "success", "rating": 1512, "rank": "expert"})

        app = web.Application()
        app.router.add_get("/rating/{platform}/{username}", rating)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]
        try:
            with patch.dict(os.environ, {"CPSTATS_API_URL": f"http://127.0.0.1:{port}", "CPSTATS_API_KEY": "demo-key"}):
                self.assertEqual((await fetch_rating("codeforces", "student"))["rating"], 1512)
                with self.assertRaises(RatingUnavailable):
                    await fetch_rating("codeforces", "missing")
                with self.assertRaises(RatingUnavailable):
                    await fetch_rating("codeforces", "../escape")
            with patch.dict(os.environ, {"CPSTATS_API_URL": "", "CPSTATS_API_KEY": ""}):
                with self.assertRaises(RatingUnavailable):
                    await fetch_rating("codeforces", "student")
        finally:
            await runner.cleanup()


class BotStartupTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_command_cogs_load_without_a_discord_token(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with patch.dict(os.environ, {
                "ENABLE_AUTO_UPDATES": "false",
                "SST_DB_PATH": str(Path(tempdir) / "bot.db"),
            }):
                bot = SSTLoungeBot()
                async with bot:
                    await bot.setup_hook()
                    self.assertEqual(
                        set(bot.cogs),
                        {"ContestCommands", "UtilityCommands", "AdminCommands", "RoleManager", "RatingCommands"},
                    )
                    command_names = {command.name for command in bot.tree.get_commands()}
                    self.assertIn("cp_rating", command_names)
                    self.assertIn("update", command_names)
