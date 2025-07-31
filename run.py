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
    """Main entry point for SST Lounge Discord Bot."""
    print("🤖 Starting SST Lounge Discord Bot...\n" + "=" * 50)

    # Check Python version
    if sys.version_info < (3, 13):
        print(f"Python 3.13+ is required. Current version: {sys.version}")
        sys.exit(1)

    try:
        # Import and run the bot
        from core import SSTLoungeBot
        import os
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv(project_root / ".env")

        # Get bot token
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            print("DISCORD_BOT_TOKEN is missing. Set it in the environment or .env file.")
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
        print(f"❌ Missing dependencies: {e}\n\n"
              "Please install dependencies:\n"
              "pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
