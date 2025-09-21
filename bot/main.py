"""
Main entry point for the AgentryLab Telegram Bot.

This module provides backward compatibility with the old main.py structure.
"""

import asyncio
from app import main

if __name__ == "__main__":
    asyncio.run(main())