"""
Simplified configuration for AgentryLab Telegram Bot.
"""

import os
from pathlib import Path

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot_username")

# AgentryLab Configuration
AGENTRYLAB_PATH = os.getenv("AGENTRYLAB_PATH", "/app/agentrylab")

# Server Configuration
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
POLLING = os.getenv("POLLING", "True").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# Limits
MAX_TOPIC_LENGTH = 200
MAX_MESSAGE_LENGTH = 4000
MAX_CONVERSATIONS_PER_USER = 3

# Messages
WELCOME_MSG = "🤖 **Welcome to AgentryLab!**\n\nHi {name}! I'm your gateway to multi-agent conversations.\n\nUse /start to begin!"
HELP_MSG = "🤖 **AgentryLab Bot Help**\n\n**Commands:**\n/start - Start a new conversation\n/help - Show this help\n/status - Check your current status\n\n**Features:**\n• Multi-agent conversations\n• Real-time streaming\n• Interactive controls"
ERROR_MSG = "❌ An error occurred. Please try again later."
NO_CONVERSATION_MSG = "❌ You don't have an active conversation."

# Callback Prefixes
PREFIX_SELECT = "select_"
PREFIX_INFO = "info_"
PREFIX_EXAMPLES = "examples_"
PREFIX_CUSTOM = "custom_"
PREFIX_CONFIRM = "confirm_"
PREFIX_BACK = "back_"
PREFIX_CANCEL = "cancel"

# Conversation States
STATE_IDLE = "idle"
STATE_WAITING_TOPIC = "waiting_topic"
STATE_ACTIVE = "active"
STATE_PAUSED = "paused"
STATE_ENDED = "ended"
