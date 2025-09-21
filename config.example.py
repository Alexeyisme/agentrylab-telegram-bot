"""
Configuration template for AgentryLab Telegram Bot

Copy this file to config.py and fill in your actual values.
"""

import os
from pathlib import Path

# Bot Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
BOT_USERNAME = "your_bot_username"  # Without @

# AgentryLab Configuration
AGENTRYLAB_PATH = "/app/agentrylab"  # Path to AgentryLab project
AGENTRYLAB_PRESETS_PATH = "/app/agentrylab/presets"  # Path to presets directory

# Server Configuration
WEBHOOK_URL = "https://your-domain.com/webhook"  # For production
WEBHOOK_PORT = 8443  # Port for webhook (production)
POLLING = True  # Set to False for webhook mode

# Database Configuration (Optional)
REDIS_URL = "redis://localhost:6379/0"  # For conversation state persistence
USE_REDIS = False  # Set to True to enable Redis

# Rate Limiting
MAX_CONVERSATIONS_PER_USER = 3  # Maximum concurrent conversations per user
MESSAGE_RATE_LIMIT = 10  # Messages per minute per user

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "bot.log"

# Admin Configuration
ADMIN_USER_IDS = []  # List of Telegram user IDs with admin access

# Feature Flags
ENABLE_CONVERSATION_HISTORY = True
ENABLE_ADMIN_COMMANDS = True
ENABLE_ANALYTICS = False

# Message Limits
MAX_MESSAGE_LENGTH = 4000  # Telegram message limit
MAX_TOPIC_LENGTH = 200  # Maximum topic length

# Timeouts
CONVERSATION_TIMEOUT = 3600  # 1 hour in seconds
USER_INPUT_TIMEOUT = 300  # 5 minutes in seconds
