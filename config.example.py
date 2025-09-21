"""
Configuration template for AgentryLab Telegram Bot

Copy this file to config.py. Values default from environment variables so you
can configure via docker-compose env without committing secrets.
"""

import os
from pathlib import Path

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")  # Get from @BotFather
BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot_username")  # Without @

# AgentryLab Configuration
AGENTRYLAB_PATH = os.getenv("AGENTRYLAB_PATH", "/app/agentrylab")
AGENTRYLAB_PRESETS_PATH = os.getenv("AGENTRYLAB_PRESETS_PATH", "/app/agentrylab/presets")

# Server Configuration
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-domain.com/webhook")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
POLLING = os.getenv("POLLING", "True").lower() == "true"

# Database Configuration (Optional)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
USE_REDIS = os.getenv("USE_REDIS", "False").lower() == "true"

# Rate Limiting
MAX_CONVERSATIONS_PER_USER = int(os.getenv("MAX_CONVERSATIONS_PER_USER", "3"))
MESSAGE_RATE_LIMIT = int(os.getenv("MESSAGE_RATE_LIMIT", "10"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# Admin Configuration
ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]

# Feature Flags
ENABLE_CONVERSATION_HISTORY = os.getenv("ENABLE_CONVERSATION_HISTORY", "True").lower() == "true"
ENABLE_ADMIN_COMMANDS = os.getenv("ENABLE_ADMIN_COMMANDS", "True").lower() == "true"
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "False").lower() == "true"

# Message Limits
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))
MAX_TOPIC_LENGTH = int(os.getenv("MAX_TOPIC_LENGTH", "200"))

# Timeouts
CONVERSATION_TIMEOUT = int(os.getenv("CONVERSATION_TIMEOUT", "3600"))
USER_INPUT_TIMEOUT = int(os.getenv("USER_INPUT_TIMEOUT", "300"))
