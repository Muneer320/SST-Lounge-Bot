# SST Lounge Discord Bot

A comprehensive Discord bot designed for **SST batch of '29** students in the **SST Lounge** server. Features an advanced contest tracking system with caching, automation, and platform filtering.

## ✨ Features

### 🏆 Advanced Contest System

- **Smart Caching**: Contests cached for 30 days, refreshed every 6 hours
- **Platform Filtering**: Support for Codeforces, CodeChef, AtCoder, LeetCode
- **Daily Commands**: `/contests_today` and `/contests_tomorrow`
- **Automated Announcements**: Daily contest updates at configurable times
- **Flexible Queries**: Filter by days (1-30), platform, and limit results
- **IST Timezone**: All times displayed in Indian Standard Time

### 🔧 Server Management

- **Admin Role Management**: Grant/revoke admin privileges (Owner only)
- **Channel Configuration**: Set contest announcement channels
- **Slash Commands**: Modern Discord interaction model
- **Permission System**: Robust admin privilege checking

### 🏗️ Architecture

- **Modular Design**: Self-contained feature modules
- **Database System**: SQLite with organized structure in `database/`
- **Background Tasks**: Automated cache refresh and announcements
- **Error Handling**: Graceful fallbacks and user-friendly messages

## 📁 Project Structure

```text
├── core/                    # Bot core and database
│   ├── bot.py              # Main bot class
│   └── database.py         # SQLite database operations
├── features/               # Modular features
│   ├── admin/              # Admin commands and role management
│   ├── contests/           # Contest system with caching
│   └── utilities/          # Basic utility commands
├── database/               # All database files
├── logs/                   # Bot logs and debugging
├── run.py                 # Bot entry point
└── requirements.txt       # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Discord Bot Token
- clist.by API credentials (required for contest features)

### Installation

1. **Clone and Setup**

   ```bash
   cd "Discord Bot"
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Environment Configuration**

   ```bash
   copy .env.example .env
   # Edit .env with your bot token and API credentials
   ```

3. **Run the Bot**
   ```bash
   python run.py
   ```

## 🎮 Commands

### Contest Commands

```bash
/contests [days:1-30] [platform] [limit:1-20]     # Show upcoming contests
/contests_today [platform] [limit:1-10]           # Today's contests
/contests_tomorrow [platform] [limit:1-10]        # Tomorrow's contests
```

**Platform Options**: `codeforces`, `codechef`, `atcoder`, `leetcode`

**Examples**:

- `/contests days:7 platform:codeforces limit:5` - Next 7 days, Codeforces only, max 5
- `/contests_today platform:leetcode` - Today's LeetCode contests
- `/contests_tomorrow limit:3` - Tomorrow's top 3 contests

### Admin Commands

```bash
/contest_setup [channel]         # Set contest announcement channel
/contest_time [time]            # Set daily announcement time (HH:MM IST)
/grant_admin [user/role]        # Grant admin privileges (Owner only)
/revoke_admin [user/role]       # Revoke admin privileges (Owner only)
/info                           # Bot information (Owner Only)
/sync                           # Sync slash commands
```

### Utility Commands

```bash
/ping                           # Check bot latency
/hello                          # Friendly greeting
/help                           # Show all commands
```

## Administrator Privileges

To use admin-only commands (`/info`, `/sync`, `/contest_setup`), you need to have the **Administrator** permission in your Discord server.

### How to Get Admin Privileges:

1. **Server Owner**: The server owner automatically has all permissions
2. **Role-based**: Server owners/admins can assign you a role with Administrator permission:
   - Server Settings → Roles → Create/Edit Role → Enable "Administrator"
   - Or assign you to an existing admin role
3. **Permission-based**: Alternatively, specific permissions can be granted for individual commands

### Admin Commands:

- `/sync` - Sync slash commands with Discord
- `/contest_setup` - Configure contest announcement channel

### Public Commands:

All other commands (like `/contests`, `/ping`, `/hello`, `/help`) are available to everyone.

## API Integration

### Clist.by API

The bot uses clist.by API to fetch contest information. Key features:

- Real-time contest data
- Multiple platform support
- Reliable scheduling information

## Development

### Adding New Features

1. Create new cogs in `bot/cogs/`
2. Add corresponding services in `bot/services/`
3. Update documentation
4. Add tests

### Testing

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and feature requests, please create an issue in the repository or contact the development team.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
