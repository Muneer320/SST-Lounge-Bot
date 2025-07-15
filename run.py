#!/usr/bin/env python3
"""
Startup script for the SST Lounge Discord Bot.
"""

import sys
import asyncio
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point."""
    print("🤖 Starting SST Lounge Discord Bot...")
    print("=" * 50)

    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your bot token.")
        print("\nSteps:")
        print("1. Copy .env.example to .env")
        print("2. Add your Discord bot token to DISCORD_BOT_TOKEN")
        print("3. Optionally add clist.by API credentials")
        sys.exit(1)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)

    try:
        # Import and run the bot
        from core import SSTLoungeBot
        import os
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv()

        # Get bot token
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            print("❌ DISCORD_BOT_TOKEN not found in .env file!")
            sys.exit(1)

        print("✅ Starting bot...")

        # Handle Windows event loop policy
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(
                asyncio.WindowsProactorEventLoopPolicy())

        # Create and run bot
        async def run_bot():
            bot = SSTLoungeBot()
            async with bot:
                await bot.start(token)

        asyncio.run(run_bot())

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\nPlease install dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
