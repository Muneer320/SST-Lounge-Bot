# SST Lounge Bot - Features Documentation

## 🏗️ Modular Architecture

The SST Lounge Bot uses a clean, modular architecture where each feature is self-contained and easy to extend.

## 📁 Directory Structure

```
features/
├── admin/
│   └── admin.py         # Administrative commands (/info, /sync)
├── contests/
│   └── contests.py      # Contest notifications and tracking
└── utilities/
    └── utilities.py     # Basic utility commands (/ping, /hello, /help)
```

## 🚀 Features Overview

### Admin Features (`features/admin/admin.py`)

- **Purpose**: Server administration and bot management
- **Commands**:
  - `/info` - Show bot statistics and server information
  - `/sync` - Sync slash commands with Discord
- **Permissions**: Requires administrator permissions
- **Usage**: Helps admins monitor bot status and manage commands

### Contest Features (`features/contests/contests.py`)

- **Purpose**: Programming contest notifications for SST batch
- **Commands**:
  - `/contests` - View upcoming programming contests
- **Features**:
  - IST timezone conversion
  - Multiple platform support (Codeforces, AtCoder, LeetCode, etc.)
  - Beautiful embed formatting
- **API**: Uses clist.by for contest data

### Utility Features (`features/utilities/utilities.py`)

- **Purpose**: Basic bot functionality and user interaction
- **Commands**:
  - `/ping` - Check bot latency and response time
  - `/hello` - Friendly greeting with bot introduction
  - `/help` - Comprehensive command listing and help
- **Usage**: General user commands for bot interaction

## 🔧 Adding New Features

To add a new feature to the bot:

1. **Create Feature Directory**:

   ```
   features/your_feature/
   └── your_feature.py
   ```

2. **Create Feature Class**:

   ```python
   from discord.ext import commands
   from discord import app_commands

   class YourFeature(commands.Cog):
       def __init__(self, bot):
           self.bot = bot

       @app_commands.command(name="yourcommand", description="Your command description")
       async def your_command(self, interaction: discord.Interaction):
           # Your command logic here
           pass

   async def setup(bot):
       await bot.add_cog(YourFeature(bot))
   ```

3. **Register in Bot**:
   Add `'features.your_feature.your_feature'` to the features list in `core/bot.py`

## 🎯 Design Principles

- **Modularity**: Each feature is independent and self-contained
- **SST Batch Focus**: All features designed for SST batch of '29 students
- **IST Timezone**: All times displayed in Indian Standard Time
- **Slash Commands Only**: Modern Discord interaction model
- **Clean Code**: Simple, readable, and maintainable code structure

## 🔍 Troubleshooting

- **Feature not loading?** Check the `core/bot.py` features list
- **Permission errors?** Ensure proper admin permission checking
- **Import errors?** Verify the feature module structure and setup function
