"""Run the contest cache pipeline with local sample data and no credentials."""

import asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytz

from core.database import SimpleDB
from features.contests.contests import ContestAPI


async def main():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    raw = []
    for offset, platform in enumerate(("codeforces.com", "atcoder.jp")):
        start = (now + timedelta(days=offset)).replace(hour=18, minute=0, second=0, microsecond=0)
        raw.append({
            "id": 10001 + offset,
            "event": f"SST Demo Contest {offset + 1}",
            "resource": platform,
            "start": start.astimezone(pytz.UTC).isoformat(),
            "duration": 7200,
            "href": "https://example.org/contest",
        })
    contests = ContestAPI()._process_contests(raw)

    class SampleAPI:
        async def fetch_upcoming_contests(self, days):
            return contests

    with tempfile.TemporaryDirectory() as tempdir:
        db = SimpleDB(str(Path(tempdir) / "demo.db"))
        await db.initialize()
        try:
            count = await db.fetch_and_cache_contests(SampleAPI())
            print(f"Cached {count} contests")
            for label, records in (
                ("Today", await db.get_contests_today()),
                ("Tomorrow", await db.get_contests_tomorrow()),
            ):
                for contest in records:
                    print(f"{label}: {contest['name']} [{contest['id']}] - {contest['start_time']}")
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())
