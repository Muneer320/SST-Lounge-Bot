# SST Lounge Bot - Features Documentation



## 🏗️ Enhanced Architecture

The SST Lounge Bot uses a clean, modular architecture where each feature is self-contained, with intelligent caching, real-time status detection, automated background tasks, and robust error handling mechanisms.

## 📁 Project Structure

```
core/                   # Core bot functionality
├── bot.py             # Main bot class and initialization
├── database.py        # SQLite operations and caching
├── updater.py         # Auto-update functionality
└── __init__.py        # Package initialization

features/              # Modular feature system
├── admin/             # Admin commands with enhanced permissions
│   └── admin.py       # Secure admin system and safe responses
├── contests/          # Contest tracking with intelligent caching
│   └── contests.py    # Platform integration and automation
├── roles/             # Automatic role management system
│   └── roles.py       # Discord Veteran role automation
└── utilities/         # Enhanced utility commands
    └── utilities.py   # File-based logging and dynamic information

utils/                 # Utility modules
└── version.py         # Dynamic version management

database/              # SQLite database files (auto-created)
logs/                  # Bot operation logs (auto-created)
.github/               # GitHub integration and templates
```

## 🚀 Features Overview

### Auto-Update System (`core/updater.py`)

- **Purpose**: Automatically update bot from GitHub repository with version tracking and admin notifications
- **Features**:
  - **Dual Update Detection**: Checks both version.json files and git commits for comprehensive update detection
  - **Version Tracking**: Semantic versioning with proper comparison of version components
  - **Manual Updates**: `/update` command allows triggering updates on demand with interactive confirmation
  - **Admin Notifications**: Automatically notifies bot administrators about available updates via DM
  - **GitHub Integration**: Checks for updates from configurable GitHub repository
  - **Configurable Repository**: Supports custom repository URL and branch through environment variables
  - **Interactive UI**: Confirmation dialogs with interactive buttons for update process
  - **Automatic Restart**: Bot restarts itself after pulling latest changes
  - **Configurable Interval**: Adjust how frequently the bot checks for updates (default: 600 seconds)
  - **Toggle Control**: Enable/disable auto-updates through environment variables
  - **Smart Comparison**: Compares local and remote version.json files for accurate update detection
  - **Safe Updates**: Error handling and rollback capabilities for failed updates
  - **Non-blocking Operations**: Uses async functions to avoid blocking bot operations
  - **Comprehensive Logging**: Detailed logs for update checks, pulls, restarts, and notifications

### Contest System (`features/contests/contests.py`)

- **Purpose**: Comprehensive contest tracking for competitive programming
- **Commands**:

  - `/contests [days] [platform] [limit]` - Upcoming contests with filters
  - `/contests_today [platform] [limit]` - Today's contests with real-time status
  - `/contests_tomorrow [platform] [limit]` - Tomorrow's contests
  - `/refresh_contests` - Manual cache refresh (Admin only)
  - `/contest_setup [channel]` - Set announcement channel (Admin only)
  - `/contest_time [time]` - Configure daily announcement time (Admin only)

- **Advanced Features**:
  - **Smart Caching**: 30-day contest data cached locally, daily refresh at 00:00 IST
  - **Real-time Status**: Live detection of contest status (⏰ Upcoming, 🔴 Running, ✅ Ended)
  - **Platform Support**: Codeforces 🟦, CodeChef 🟡, AtCoder 🟠, LeetCode 🟢
  - **Background Automation**: Daily cache refresh and configurable announcements
  - **Admin Management**: Role-based permissions and manual refresh capabilities
  - **IST Timezone**: All times displayed in Indian Standard Time
  - **Database Integration**: SQLite with optimized indexing for instant responses

### Admin System (`features/admin/admin.py`)

- **Purpose**: Bot administration, permission management, and system monitoring
- **Commands**:

  - `/info` - Bot statistics with dynamic version information
  - `/sync` - Sync slash commands with enhanced error handling
  - `/grant_admin <user/role>` - Grant bot admin privileges (Server Owner only)
  - `/revoke_admin <user/role>` - Revoke bot admin privileges (Server Owner only)
  - `/list_admins` - List all bot admins with grant history
  - `/update [schedule]` - Manual bot updates with interactive confirmation

- **Enhanced Features**:
  - **Three-Tier Permission System**: Server owner → Discord admins → Bot admins
  - **Safe Response Handling**: Intelligent interaction management prevents "already acknowledged" errors
  - **Dynamic Version Display**: Real-time bot version information from version.json
  - **Interactive Updates**: User-friendly update confirmation with buttons
  - **Comprehensive Error Handling**: Graceful fallbacks and informative error messages
  - **Secure Access Control**: Role-based permissions with database persistence

### Advanced Logging System (`features/utilities/utilities.py`)

- **Purpose**: Comprehensive log management and export functionality
- **Commands**:

  - `/logs [lines] [hours] [minutes] [level]` - Export logs as downloadable files
  - **Parameters**:
    - `lines`: Number of lines (1-1000, default: 50)
    - `hours`: Last N hours (must be positive)
    - `minutes`: Last N minutes (must be positive, overrides hours)
    - `level`: Filter by log level (INFO/WARNING/ERROR/DEBUG)

- **Advanced Features**:
  - **File-Based Export**: Downloads organized text files instead of Discord embeds
  - **Enhanced Capacity**: Support for up to 1000 lines (10x increase from previous limit)
  - **Smart Validation**: Prevents negative time values with helpful error messages
  - **Professional Formatting**: Headers with metadata, timestamps, and organized content
  - **Intelligent Filtering**: Time-based and level-based log filtering
  - **Dynamic Naming**: Auto-generated filenames with timestamps and applied filters
  - **Autocomplete Support**: Log level suggestions for improved user experience

### Role Management System (`features/roles/roles.py`)

- **Purpose**: Automatic role assignment based on Discord account age and criteria
- **Commands**:

  - `/check_veterans` - Manual veteran role check and assignment (Admin only)
  - `/veteran_info` - Show Discord Veteran role criteria and user's qualification status

- **Automatic Features**:
  - **Discord Veteran Role**: Automatically assigns role to members with 5+ year old Discord accounts
  - **On-Join Detection**: New members are checked and assigned veteran role immediately if qualified
  - **Daily Background Checks**: Runs daily to check existing members who may have become eligible
  - **Smart Role Creation**: Creates the "Discord Veteran" role automatically if it doesn't exist
  - **Rate Limit Protection**: Includes delays to avoid Discord API rate limits
  - **Comprehensive Logging**: Detailed logs for all role assignments and checks

### Utility System (`features/utilities/utilities.py`)

- **Purpose**: Essential bot functionality and user interaction
- **Commands**:
  - `/ping` - Check bot latency and response time
  - `/hello` - Friendly greeting with bot introduction
  - `/help` - Comprehensive command listing and documentation
  - `/contribute` - Get information about contributing to the bot development
- **Usage**: General user commands accessible to all server members

## 🔧 Adding New Features

To add a new feature to the bot:

1. **Create Feature Directory**:

   ```
   features/your_feature/
   └── your_feature.py
   ```

2. **Create Feature Class**:

   ```python
   from discord.ext import commands, tasks
   from discord import app_commands
   import discord

   class YourFeature(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
           # Start background tasks if needed
           # self.your_background_task.start()

       @app_commands.command(name="yourcommand", description="Your command description")
       async def your_command(self, interaction: discord.Interaction):
           # Your command logic here
           await interaction.response.send_message("Command executed!")

       # Optional: Background task example
       @tasks.loop(hours=24)
       async def your_background_task(self):
           # Background task logic
           pass

       def cog_unload(self):
           # Clean up background tasks
           # self.your_background_task.cancel()
           pass

   async def setup(bot):
       await bot.add_cog(YourFeature(bot))
   ```

3. **Register in Bot**:
   Add your feature to the features list in `core/bot.py`

## 🎯 Design Principles

- **Modularity**: Each feature is independent with clear separation of concerns
- **SST Batch Focus**: All features designed specifically for SST batch of '29 students
- **Performance**: Intelligent caching and background tasks for optimal response times
- **Real-time Updates**: Live status detection and automated refresh cycles
- **IST Timezone**: All times displayed in Indian Standard Time for local relevance
- **Modern Discord**: Slash commands only with rich embed formatting
- **Admin Control**: Granular permission system with owner and admin tiers
- **Database Integration**: SQLite with optimized queries and proper indexing
- **Error Handling**: Graceful fallbacks and comprehensive logging

## 🔍 Technical Implementation

- **Caching Strategy**: 30-day data cache with daily refresh at 00:00 IST
- **Status Detection**: Real-time contest status analysis with duration calculations
- **Background Tasks**: `@tasks.loop` for automated cache refresh and announcements
- **Database Design**: Indexed SQLite tables for sub-millisecond query responses
- **API Integration**: Reliable clist.by integration with proper error handling
- **Permission System**: Role-based access control with admin privilege management

## 🚀 Performance Features

- **Smart Caching**: Reduces API calls by 95% while maintaining data freshness
- **Optimized Queries**: Database indexing enables instant contest lookups
- **Background Processing**: Non-blocking daily refresh and announcement tasks
- **Memory Efficiency**: Selective data loading and cleanup procedures
- **Error Recovery**: Automatic retry mechanisms and fallback strategies

## 📈 Performance & Monitoring

### Database Performance

- **Query Optimization**: All database queries use proper indexing for sub-millisecond responses
- **Connection Management**: Persistent SQLite connections with proper cleanup
- **Cache Strategy**: 30-day contest data cached locally, reducing API calls by 95%

### Background Tasks

- **Daily Cache Refresh**: Automated at 00:00 IST to ensure fresh contest data
- **Role Management**: Daily veteran role checks for existing members
- **Announcement System**: Configurable daily contest announcements

### Error Handling & Logging

- **Comprehensive Logging**: All operations logged to `logs/sst_lounge.log`
- **Graceful Fallbacks**: API failures handled with cached data
- **Rate Limit Protection**: Built-in delays for Discord API compliance
- **Database Resilience**: Automatic connection recovery and error handling

### Bot Administration

- **Three-Tier Permission System**: Server owner → Discord admins → Bot admins
- **Transparent Management**: All admin grants tracked with timestamps and granter info
- **Live Monitoring**: `/info` command provides real-time bot statistics
- **Command Sync**: Easy slash command synchronization with `/sync`

## 🛡️ Security & Best Practices

- **Environment Variables**: All sensitive data stored in `.env` file
- **Permission Validation**: Every admin command validates user permissions
- **Database Security**: Parameterized queries prevent SQL injection
- **Error Privacy**: User-facing errors don't expose internal details
- **Graceful Shutdown**: Proper cleanup of connections and background tasks

## 🔍 Troubleshooting

- **Feature not loading?** Check the `core/bot.py` features list and ensure proper setup function
- **Permission errors?** Verify admin role configuration and permission decorators
- **Database issues?** Check SQLite connection and table initialization
- **Background tasks?** Ensure tasks are properly started in `__init__` and cancelled in `cog_unload`
- **API errors?** Verify clist.by credentials and network connectivity
