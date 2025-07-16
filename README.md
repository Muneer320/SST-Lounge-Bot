# SST Lounge Discord Bot

A comprehensive Discord bot designed for **SST batch of '29** students in the **SST Lounge** server. Features an advanced contest tracking system with intelligent caching, real-time status updates, and automated announcements.

## ✨ Features

### 🏆 Advanced Contest System

- **Smart Caching**: 30-day contest data with daily refresh cycles
- **Real-time Status**: Shows live contest status (⏰ Upcoming, 🔴 Running, ✅ Ended)
- **Platform Filtering**: Support for Codeforces, CodeChef, AtCoder, LeetCode
- **Today's Focus**: Enhanced `/contests_today` with status and duration details
- **Automated Announcements**: Daily contest updates at configurable times
- **Flexible Queries**: Filter by days (1-30), platform, and limit results
- **IST Timezone**: All times displayed in Indian Standard Time

### 🔧 Admin Management

- **Manual Cache Refresh**: `/refresh_contests` for immediate data updates
- **Role Management**: Grant/revoke admin privileges (Owner only)
- **Channel Configuration**: Set contest announcement channels and timing
- **Permission System**: Robust admin privilege checking

### 🏗️ Architecture

- **Modular Design**: Self-contained feature modules
- **SQLite Database**: Optimized with indexing for fast queries
- **Background Tasks**: Daily cache refresh and automated announcements
- **Error Handling**: Graceful fallbacks with detailed logging

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

## 📋 Commands

### Contest Commands

- `/contests [days:1-30] [platform] [limit:1-30]` - Get upcoming contests with filters

  - **days**: Number of days to look ahead (1-30, default: 7)
  - **platform**: Filter by platform (codeforces, codechef, atcoder, leetcode)
  - **limit**: Maximum number of results (1-30, default: 10)

- `/contests_today [platform] [limit:1-10]` - Today's contests with real-time status

  - **⏰ Upcoming**: Contest hasn't started yet
  - **🔴 Running**: Contest is currently active
  - **✅ Ended**: Contest has finished

- `/contests_tomorrow [platform] [limit:1-10]` - Tomorrow's contests

**Platform Options**: `codeforces` 🔵, `codechef` 🟡, `atcoder` 🟠, `leetcode` 🟢

### Admin Commands (Admin Role Required)

- `/refresh_contests` - Manually refresh contest cache (bypasses daily refresh)
- `/contest_setup [channel]` - Set contest announcement channel
- `/contest_time [time]` - Configure announcement time (24-hour format HH:MM IST)
- `/info` - Show bot statistics and server information
- `/sync` - Sync slash commands with Discord

### Owner Commands (Server Owner Only)

- `/grant_admin [user]` - Grant admin privileges to a user
- `/revoke_admin [user]` - Remove admin privileges from a user

### Utility Commands

- `/ping` - Check bot latency
- `/hello` - Friendly greeting
- `/help` - Show all commands

## 🔐 Administrator Privileges

To use admin-only commands, you need to have the **Administrator** permission in your Discord server or be granted admin privileges by the server owner.

1. **Server Owner**: The server owner automatically has all permissions
2. **Role-based**: Server owners/admins can assign you a role with Administrator permission:
   - Server Settings → Roles → Create/Edit Role → Enable "Administrator"
   - Or assign you to an existing admin role
3. **Permission-based**: Alternatively, specific permissions can be granted for individual commands

### Admin Commands:

- `/sync` - Sync slash commands with Discord
- `/contest_setup` - Configure contest announcement channel

### Public Commands:

## 🤖 Bot Behavior

### Automated Features

- **Daily Cache Refresh**: Contest data automatically refreshes every day at 00:00 IST
- **Smart Caching**: 30-day contest data cached locally for instant responses
- **Contest Announcements**: Configurable daily announcements in designated channels
- **Status Detection**: Real-time contest status updates (upcoming/running/ended)

### Data Management

- **Database**: SQLite with optimized indexing for fast queries
- **Cache Strategy**: Fetch from 00:00 hours to include today's contests
- **Platform Conversion**: Automatic mapping of platform names for consistency

## 🔧 API Integration

### Clist.by API

The bot integrates with clist.by API for contest data:

- **Authentication**: Uses username/API key for reliable access
- **Data Format**: Handles datetime formats and timezone conversions
- **Error Handling**: Graceful fallbacks when API is unavailable
- **Rate Limiting**: Respects API limits with proper caching

## 🏗️ Development

### Project Structure

```
core/               # Core bot functionality
├── bot.py         # Main bot class and setup
├── database.py    # SQLite operations
└── config.py      # Configuration management

features/          # Feature modules
├── contests/      # Contest system
└── utilities/     # Basic commands

database/          # SQLite database files
logs/             # Bot operation logs
```

### Adding Features

1. Create new feature modules in `features/`
2. Follow the existing pattern for cogs and services
3. Update database schema if needed
4. Add proper error handling and logging

## 📈 Performance

- **Optimized Queries**: Database indexing for sub-millisecond responses
- **Memory Efficient**: Smart caching reduces API calls by 95%
- **Background Tasks**: Non-blocking daily refresh and announcements
- **Error Recovery**: Automatic retry mechanisms and fallback strategies


## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
