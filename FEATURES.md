# Feature and module guide

| Module | Responsibility |
|---|---|
| `core/bot.py` | Configures Discord intents, SQLite, command modules and background release checks |
| `core/database.py` | Persists guild settings, bot admin grants, contest cache and delivered release notices |
| `core/updater.py` | Compares published `version.json` files and sends each directly granted admin one DM per version |
| `features/contests/contests.py` | Fetches contests from clist.by, converts times to IST, and posts listings and announcements |
| `features/ratings/ratings.py` | Calls a separately hosted CPStats API for `/cp_rating` |
| `features/roles/roles.py` | Assigns and describes the five-year Discord Veteran role |
| `features/admin/admin.py` | Handles bot admin grants, server information and read-only `/update` checks |
| `features/utilities/utilities.py` | Offers help, ping, greeting, contribution links and optional admin log export |

The contest cache uses clist's stable numeric IDs. A six-hour background refresh reduces API calls; daily announcements are checked every five minutes and marked sent by IST date. The release checker is read-only. Deploy a new version from the host with the instructions in [README.md](README.md).

`demo.py` runs the contest parser and SQLite cache using local sample data. `tests/` verifies the same pipeline, durable settings, once-per-version notices, the rating API boundary and loading every command module without a Discord token.

Log export is disabled by default because the log may contain member and server information. CPStats ratings require a working companion API instance and a bearer key; contest listings do not use CPStats.
