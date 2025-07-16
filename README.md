# SST Lounge Discord Bot

A comprehensive Discord bot designed for **SST batch of '29** students in the **SST Lounge** server. Provides various functionalities to facilitate server management, student coordination, and more. 

## Features

### 🏆 Contest Tracking

- **Contest Notifications**: Automatically fetches and announces upcoming contests from major CP platforms
  - Codeforces, CodeChef, AtCoder, LeetCode
- **Daily Contest Updates**: Scheduled daily announcements in designated channels
- **IST Timezone**: All times displayed in Indian Standard Time

### 🔧 Server Management

- **Channel configuration** for various features
- **Role-based permissions** for different functionalities
- **Slash commands** for easy interaction
- **Modular architecture** for future expansions
  

## 🏗️ Modular Architecture

The SST Lounge Bot features a **clean, modular architecture** designed for easy maintenance and extensibility:

- **📁 Features Directory**: Each feature is self-contained in its own module
- **🔧 Easy Extension**: Add new features without touching existing code
- **🧹 Clean Separation**: Admin, contest, and utility features are completely separate
- **📖 Documentation**: Comprehensive feature documentation in `FEATURES.md`

See `FEATURES.md` for detailed information about adding new features and the current feature architecture.

## Project Structure

```text
├── core/                    # Core bot setup & database
├── features/                # Modular feature cogs
├── tests/                   # Unit tests (pytest)
├── run.py                   # Bot entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── FEATURES.md              # Feature documentation
└── README.md                # Project overview
```

## Quick Start

### Prerequisites

- Python 3.8+
- Discord Bot Token
- clist.by API credentials (optional for enhanced features)

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
   # Edit .env with your bot token and API keys
   ```

3. **Run the Bot**
   ```bash
   python run.py
   ```

## Configuration

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable necessary intents (Message Content Intent, Server Members Intent)

### Bot Permissions

The bot requires the following permissions:

- Send Messages
- Embed Links
- Read Message History
- Manage Messages (for cleanup features)

## Commands

### Contest Commands

- `/contests [days]` - Show upcoming contests (default: 3 days, IST timezone)

### Utility Commands

- `/ping` - Check bot response time
- `/hello` - Get a friendly greeting
- `/help` - Show all available commands

### Admin Commands

- `/sync` - Sync slash commands with Discord
- `/sync` - Sync slash commands (Admin only)

## Administrator Privileges

To use admin-only commands (`/sync`, `/contest_setup`), you need to have the **Administrator** permission in your Discord server.

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

All other commands (like `/info`, `/contests`, `/ping`, `/hello`, `/help`) are available to everyone.

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
