# SST Lounge Bot

An unofficial Discord bot for the SST Batch '29 Lounge. It lists programming contests from clist.by, posts daily announcements, manages a veteran role, and lets server owners grant bot admin access. An optional `/cp_rating` command reads public ratings from the separate [CPStats API](https://github.com/Muneer320/CPStats-API).

## Try it without credentials

The local demo exercises the real contest parser and SQLite cache with sample data. It makes no Discord or external API calls.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.lock.txt
.\.venv\Scripts\python demo.py
.\.venv\Scripts\python -m unittest discover -s tests -v
```

On macOS or Linux, use `.venv/bin/python` instead. The demo prints one contest for today and one for tomorrow in IST. Tests cover the cache, stable contest IDs, release notices, API client and command module startup.

## Run in Discord

Python 3.13+ and a Discord bot token are required. Create a bot in the [Discord developer portal](https://discord.com/developers/applications), enable the **Server Members** and **Message Content** privileged intents, and invite it with `bot` and `applications.commands` scopes. Give it **Manage Roles** only if you use veteran role assignment; its own role must be above the veteran role.

1. Copy `.env.example` to `.env` and set `DISCORD_BOT_TOKEN`.
2. Set `CLIST_API_USERNAME` and `CLIST_API_KEY` for the contest commands. Clist.by requires an API key for API access.
3. Run `python -m pip install -r requirements.lock.txt` and `python run.py`.

The token may also be provided as an environment variable. The bot stores settings, cached contests and notification history in `database/sst_lounge.db`; logs go to `logs/sst_lounge.log`. Both paths are ignored by Git.

### Docker Compose

After creating `.env`, run:

```sh
docker compose up --build -d
docker compose logs -f bot
```

Compose runs one bot process, restarts it after a failure or host restart, and keeps SQLite and logs in named volumes. To deploy a new commit, run `git pull --ff-only` followed by `docker compose up --build -d`. To stop it, run `docker compose down`. Do not run a local `python run.py` at the same time with the same bot token.

## Commands

| Command | Behavior |
|---|---|
| `/contests`, `/contests_today`, `/contests_tomorrow` | Show cached or newly fetched contests in IST, with platform filters |
| `/contest_setup`, `/contest_time`, `/refresh_contests` | Configure and refresh daily announcements; requires admin access |
| `/cp_rating` | Fetch a public handle's rating from CPStats API when configured |
| `/veteran_info`, `/check_veterans` | Inspect or assign the veteran role |
| `/grant_admin`, `/revoke_admin`, `/list_admins` | Manage bot admin grants; grants and revocations require the server owner |
| `/update` | Check published `version.json` and show redeployment instructions; requires admin access |
| `/logs` | Export logs only when the host opts in; requires admin access |
| `/ping`, `/hello`, `/help`, `/contribute`, `/info` | Utility and project information |

Contest cache refresh runs every six hours. Announcements are checked every five minutes and sent once per IST calendar day at the configured time. The bot checks the repository's `version.json` for newer releases and sends each directly granted admin one DM per version. It does not replace its own running process. Role grants do not create notification recipients because a role is not a DM destination.

### Optional CPStats API

Set `CPSTATS_API_URL` to the running API base URL and `CPSTATS_API_KEY` to that API's bearer token. The public CPStats deployment is currently not verified, so `/cp_rating` reports a configuration or availability error until a working instance is supplied. The bot does not use CPStats for contest listings; those come from clist.by.

### Privacy and limits

`/logs` is disabled by default because logs can contain member IDs, names and server information. Set `ENABLE_LOG_EXPORT=true` only if your server's operators have decided to allow admin downloads of that data. The local database and logs are not tracked by Git. This repo includes an offline demo and tests; a live Discord connection and the optional CPStats deployment require credentials and were not verified here.

See [FEATURES.md](FEATURES.md) for module details and [CHANGELOG.md](CHANGELOG.md) for release history. Licensed under [MIT](LICENSE).
