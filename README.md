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

### 🎭 Automatic Role Management

- **Discord Veteran Role**: Automatically assigns "Discord Veteran" role to members with 5+ year old Discord accounts
- **On-Join Detection**: New members are automatically checked and assigned veteran role if qualified
- **Daily Role Checks**: Background task runs daily to check existing members
- **Manual Role Check**: Admin command to manually trigger veteran role assignment
- **Smart Role Creation**: Automatically creates the role if it doesn't exist

### 🔄 Auto-Update System

- **GitHub Integration**: Automatically checks for updates from a configurable GitHub repository
- **Smart Detection**: Uses semantic versioning and git commit comparison for update detection
- **Configurable Settings**: Set custom repository URL, branch, and check intervals
- **Admin Notifications**: Automatically notifies bot administrators about available updates
- **Manual Updates**: `/update` command allows triggering updates on demand with confirmation
- **Safe Restart**: Automatic bot restart after successful updates
- **Toggle Control**: Easily enable or disable auto-updates via environment variables

###️ Bot Admin System

- **Three-Tier Permission System**: Server owner → Discord admins → Bot admins
- **Bot-Level Privileges**: Custom admin system that doesn't affect Discord server permissions
- **User and Role Support**: Grant admin privileges to specific users or entire roles
- **Owner Control**: Only server owners can grant/revoke bot admin privileges
- **Admin Transparency**: List all bot admins with grant history

### �🔧 Admin Management

- **Manual Cache Refresh**: `/refresh_contests` for immediate data updates
- **Bot Admin Management**: Grant/revoke bot-level admin privileges (Owner only)
- **Channel Configuration**: Set contest announcement channels and timing
- **Permission System**: Robust three-tier admin privilege checking

### 🏗️ Architecture

- **Modular Design**: Self-contained feature modules
- **SQLite Database**: Optimized with indexing for fast queries
- **Background Tasks**: Daily cache refresh and automated announcements
- **Error Handling**: Graceful fallbacks with detailed logging

## 📁 Project Structure

```text
├── core/                    # Bot core and database
│   ├── bot.py              # Main bot class
│   ├── database.py         # SQLite database operations
│   └── updater.py          # Auto-update functionality
├── features/               # Modular features
│   ├── admin/              # Admin commands and role management
│   ├── contests/           # Contest system with caching
│   ├── roles/              # Automatic role management system
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
   # Configure auto-update settings (repository URL, branch, interval)
   ```

3. **Bot Permissions Setup**

   When inviting the bot to your Discord server, ensure it has these permissions:

   - **Manage Roles**: Required for automatic Discord Veteran role assignment
   - **View Channels**: Basic permission to see channels
   - **Send Messages**: To send contest announcements and command responses
   - **Use Slash Commands**: Modern Discord command interface
   - **Manage Server**: For admin features (optional, for server owners only)

   **Important**: The bot must have a role higher than the "Discord Veteran" role in the role hierarchy to assign it to members.

4. **Run the Bot**
   ```bash
   python run.py
   ```

## 📋 Commands

### Contest Commands

- `/contests [days:1-30] [platform] [limit:1-30]` - Get upcoming contests with filters

  - **days**: Number of days to look ahead (1-30, default: 3)
  - **platform**: Filter by platform (codeforces, codechef, atcoder, leetcode)
  - **limit**: Maximum number of results (1-20, default: all)

- `/contests_today [platform] [limit:1-10]` - Today's contests with real-time status

  - **⏰ Upcoming**: Contest hasn't started yet
  - **🔴 Running**: Contest is currently active
  - **✅ Ended**: Contest has finished

- `/contests_tomorrow [platform] [limit:1-10]` - Tomorrow's contests

**Platform Options**: `codeforces` 🔵, `codechef` 🟡, `atcoder` 🟠, `leetcode` 🟢

### Admin Commands (Bot Admin Required)

- `/refresh_contests` - Manually refresh contest cache (bypasses daily refresh)
- `/contest_setup [channel]` - Set contest announcement channel
- `/contest_time [time]` - Configure announcement time (24-hour format HH:MM IST)
- `/check_veterans` - Manually check and assign Discord Veteran roles to qualifying members
- `/info` - Show bot statistics and server information
- `/sync` - Sync slash commands with Discord
- `/list_admins` - List all bot admins (shows grant history)
- `/update` - Update the bot to the latest version from GitHub

### Owner Commands (Server Owner Only)

- `/grant_admin [user] or [role]` - Grant bot admin privileges to a user or role
- `/revoke_admin [user] or [role]` - Remove bot admin privileges from a user or role

### Utility Commands

- `/ping` - Check bot latency
- `/hello` - Friendly greeting
- `/help` - Show all commands
- `/contribute` - Get information about contributing to the bot development

### Role Information Commands

- `/veteran_info` - Show Discord Veteran role criteria and your qualification status

## 🤝 Contributing

We welcome contributions from the SST Batch '29 community! Whether you want to report bugs, suggest features, or contribute code, here's how you can help:

### 🐛 Report Bugs

- Use the `/contribute` command in Discord for quick access to our GitHub
- Create an [issue](https://github.com/Muneer320/SST-Lounge-Bot/issues/new/choose) using our bug report template
- Include:
  - Clear description of the bug
  - Steps to reproduce the issue
  - Expected vs actual behavior
  - Discord command that caused the issue

### 💡 Suggest Features

- Use `/contribute` command for guidelines
- Create a [feature request](https://github.com/Muneer320/SST-Lounge-Bot/issues/new/choose) using our template
- Include:
  - Clear description of the feature
  - How it would benefit the batch
  - Any implementation ideas you have

### 👨‍💻 Code Contributions

1. Fork the repository: https://github.com/Muneer320/SST-Lounge-Bot
2. Read our [Contributing Guide](.github/CONTRIBUTING.md) for detailed instructions
3. Create a feature branch: `git checkout -b feature-name`
4. Make your changes and test them
5. Submit a pull request using our PR template

### 📋 Areas We Need Help With

- Additional utility commands for batch coordination
- Documentation and help text improvements
- Bug fixes and performance optimizations

## 🔐 Bot Administrator Privileges

The bot uses a **three-tier permission system** for administrative commands:

### Permission Levels (in order of precedence):

1. **Server Owner**: The Discord server owner automatically has all bot admin privileges
2. **Discord Administrators**: Users with Discord's Administrator permission have bot admin access
3. **Bot Admins**: Users or roles specifically granted bot admin privileges by the server owner

### Bot Admin System:

- **Bot-Level Only**: Bot admin privileges don't affect Discord server permissions
- **Granular Control**: Server owners can grant admin access without giving Discord admin permissions
- **User and Role Support**: Grant privileges to individual users or entire roles
- **Transparent Management**: Use `/list_admins` to see all current bot admins and who granted them access

### How to Grant Bot Admin Access:

1. **Must be Server Owner**: Only the Discord server owner can grant/revoke bot admin privileges
2. **Grant to User**: `/grant_admin user:@username` - Gives that specific user bot admin access
3. **Grant to Role**: `/grant_admin role:@rolename` - Gives all members of that role bot admin access
4. **View Admins**: `/list_admins` - Shows all current bot admins with grant history
5. **Revoke Access**: `/revoke_admin user:@username` or `/revoke_admin role:@rolename`

## 🤖 Bot Behavior

### Automated Features

- **Daily Cache Refresh**: Contest data automatically refreshes every day at 00:00 IST
- **Discord Veteran Roles**: Daily check and assignment of veteran roles to qualifying members
- **Smart Caching**: 30-day contest data cached locally for instant responses
- **Contest Announcements**: Configurable daily announcements in designated channels
- **Status Detection**: Real-time contest status updates (upcoming/running/ended)
- **Member Join Detection**: Automatic veteran role assignment for new members

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

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
