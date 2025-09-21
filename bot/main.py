"""
Main entry point for the AgentryLab Telegram Bot.

This module provides backward compatibility with the old main.py structure.
"""

import sys
from pathlib import Path

# Add the bot directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())