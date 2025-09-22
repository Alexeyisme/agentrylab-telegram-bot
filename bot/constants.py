"""
Constants and configuration for the AgentryLab Telegram Bot.

This module centralizes all magic strings, configuration values, and constants
to improve maintainability and reduce code duplication.
"""

from enum import Enum
from typing import Dict, List


class Messages:
    """User-facing messages and error messages."""

    # Error messages
    BOT_NOT_INITIALIZED = "❌ Bot not properly initialized. Please try again later."
    NO_ACTIVE_CONVERSATION = "❌ You don't have an active conversation."
    NO_PAUSED_CONVERSATION = "❌ You don't have a paused conversation to resume."
    NO_CONVERSATION_TO_STOP = "❌ You don't have an active conversation to stop."
    NO_CONVERSATION_TO_PAUSE = "❌ You don't have an active conversation to pause."
    NO_PRESET_SELECTED = "❌ No preset selected. Please start over with /start"
    NO_TOPIC_SELECTED = "❌ No topic selected. Please try again."
    NO_CONVERSATION_FOUND = "❌ No active conversation found."
    NO_PAUSED_CONVERSATION_FOUND = "❌ No paused conversation found."
    ERROR_OCCURRED = "❌ An error occurred. Please try again later."
    UNKNOWN_ACTION = "❌ Unknown action. Please try again."
    OPERATION_CANCELLED = "❌ Operation cancelled."

    # Success messages
    CONVERSATION_STARTED = "🚀 **Conversation Started!**"
    CONVERSATION_PAUSED = "⏸️ **Conversation Paused**"
    CONVERSATION_RESUMED = "▶️ **Conversation Resumed**"
    CONVERSATION_STOPPED = "⏹️ **Conversation Stopped**"
    MESSAGE_SENT = "✅ **Message sent!**"
    CONVERSATION_COMPLETED = "✅ **Conversation Completed!**"

    # Status messages
    WAITING_FOR_TURN = "⏳ Please wait for your turn to speak in the conversation."
    USER_TURN = "👤 **It's your turn!** What would you like to say?"
    CONVERSATION_ENDED = "The discussion has ended. Thank you for participating!"
    USE_START_COMMAND = "Use /start to begin a new conversation."

    # Welcome messages
    WELCOME_TITLE = "🤖 **Welcome to AgentryLab!**"
    WELCOME_DESCRIPTION = "Hi {name}! I'm your gateway to multi-agent conversations."
    WELCOME_FEATURES = """**What can I do?**
• Start debates between AI agents
• Run stand-up comedy sessions
• Conduct therapy sessions
• Facilitate brainstorming sessions
• And much more!"""
    WELCOME_INSTRUCTIONS = """**How to get started:**
1. Choose a conversation type
2. Enter your topic
3. Watch AI agents interact in real-time
4. Join in when it's your turn!"""
    WELCOME_CTA = "Click the button below to see available conversation types!"

    # Help messages
    HELP_TITLE = "📚 **Available Commands:**"
    HELP_GETTING_STARTED = """**Getting Started:**
/start - Start the bot and see welcome message
/help - Show this help message
/presets - List available conversation types"""
    HELP_CONVERSATION_MANAGEMENT = """**Conversation Management:**
/status - Show your current conversation status
/pause - Pause an active conversation
/resume - Resume a paused conversation
/stop - Stop an active conversation"""
    HELP_USAGE = """**How to Use:**
1. Use /start to begin
2. Choose a conversation type from the buttons
3. Enter your topic when prompted
4. Watch AI agents interact in real-time
5. Join in when it's your turn!"""
    HELP_CONTROLS = """**Conversation Controls:**
• Use inline buttons to control conversations
• Type messages when it's your turn
• Use commands to pause/resume/stop conversations"""
    HELP_SUPPORT = "**Need help?** Contact @your_support_username"

    # Preset messages
    CHOOSE_CONVERSATION_TYPE = "🎭 **Choose a Conversation Type:**"
    SELECT_PRESET_DESCRIPTION = "Select a preset to start a multi-agent conversation:"
    CLICK_PRESET_TO_START = "Click on a preset below to get started!"
    NO_PRESETS_AVAILABLE = (
        "❌ No presets available. Please check your AgentryLab configuration."
    )
    PRESET_INFO_TITLE = "ℹ️ **About Presets**"
    PRESET_INFO_DESCRIPTION = """Presets are pre-configured conversation types that define:

• **Agents**: AI characters with specific roles
• **Scheduler**: How agents take turns
• **Prompts**: Instructions for each agent
• **Tools**: Available tools and resources

Each preset is designed for a specific type of conversation, 
from debates to therapy sessions to brainstorming.

Click on a preset above to see more details and examples!"""

    # Topic input messages
    ENTER_TOPIC_TITLE = "**Enter your topic:**"
    ENTER_TOPIC_DESCRIPTION = "Type your topic below. For example:"
    ENTER_TOPIC_INSTRUCTION = "Just type your message and send it!"
    TOPIC_CONFIRMATION_TITLE = "Ready to start the conversation? Click below to begin!"
    TOPIC_TOO_SHORT = "Topic must be at least 3 characters long."
    TOPIC_TOO_LONG = "Topic is too long. Please keep it under 500 characters."
    TOPIC_INAPPROPRIATE = (
        "Topic contains inappropriate content. Please choose a different topic."
    )
    TOPIC_INVALID_CHARS = "Topic contains invalid characters. Please use only letters, numbers, and basic punctuation."
    TOPIC_REPETITIVE = "Topic contains too much repetition. Please be more specific."

    # Conversation messages
    CONVERSATION_SETUP = """⏳ Setting up agents...
🔄 Initializing conversation...

The conversation will start shortly!"""
    CONVERSATION_REAL_TIME = "The AI agents are now discussing your topic. You'll see their messages in real-time below."
    CONVERSATION_SEPARATOR = "---"
    CONVERSATION_CONTINUE = "The AI agents will continue the discussion."
    CONVERSATION_INPUT_ADDED = "Your input has been added to the conversation."

    # Status messages
    STATUS_TITLE = "📊 **Your Conversation Status:**"
    STATUS_NO_ACTIVE = "📭 You have no active conversations. Use /start to begin!"
    STATUS_STATE = "**State:** {state}"
    STATUS_PRESET = "**Preset:** {preset}"
    STATUS_TOPIC = "**Topic:** {topic}"
    STATUS_CONVERSATION_ID = "**Conversation ID:** {conversation_id}"
    STATUS_LAST_ACTIVITY = "**Last Activity:** {last_activity}"

    # Regular message responses
    HELLO_MESSAGE = """🤖 **Hello!** I'm your AgentryLab assistant.

To get started, use one of these commands:
• /start - Start a new conversation
• /presets - See available conversation types
• /help - Get help and see all commands

Or just type /start to begin!"""


class CallbackPrefixes:
    """Callback data prefixes for inline keyboards."""

    PRESET = "preset_"
    SELECT = "select_"
    EXAMPLES = "examples_"
    EXAMPLE = "example_"
    CUSTOM = "custom_"
    START = "start_"
    EDIT = "edit_"
    INFO = "info_"

    # Navigation callbacks
    BACK_TO_PRESETS = "back_to_presets"
    PRESET_INFO = "preset_info"
    CANCEL = "cancel"
    CATEGORY_HEADER = "category_header"


class ConversationStates:
    """Conversation state constants."""

    IDLE = "idle"
    SELECTING_PRESET = "selecting_preset"
    ENTERING_TOPIC = "entering_topic"
    CONFIRMING_TOPIC = "confirming_topic"
    STARTING_CONVERSATION = "starting_conversation"
    IN_CONVERSATION = "in_conversation"
    WAITING_FOR_USER_INPUT = "waiting_for_user_input"
    CONVERSATION_PAUSED = "conversation_paused"
    CONVERSATION_ENDED = "conversation_ended"
    ERROR = "error"


class EventTypes:
    """Conversation event types."""

    CONVERSATION_STARTED = "conversation_started"
    AGENT_MESSAGE = "agent_message"
    USER_MESSAGE = "user_message"
    USER_TURN = "user_turn"
    CONVERSATION_COMPLETED = "conversation_completed"
    ERROR = "error"
    MODERATOR_ACTION = "moderator_action"
    SUMMARY_UPDATE = "summary_update"


class Roles:
    """Agent roles in conversations."""

    USER = "user"
    MODERATOR = "moderator"
    SUMMARIZER = "summarizer"
    AGENT = "agent"


class Emojis:
    """Emoji constants for consistent usage."""

    # Status emojis
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    PAUSE = "⏸️"
    PLAY = "▶️"
    STOP = "⏹️"

    # Navigation emojis
    BACK = "🔙"
    CANCEL = "❌"
    SELECT = "✅"
    EDIT = "✏️"
    CUSTOM = "✏️"
    EXAMPLES = "📝"

    # Conversation emojis
    USER = "👤"
    AGENT = "🤖"
    MODERATOR = "👨‍⚖️"
    SUMMARIZER = "📝"
    CONVERSATION = "💬"
    START = "🚀"
    COMPLETE = "✅"

    # Preset emojis
    PRESETS = "🎭"
    DEBATES = "⚖️"
    STAND_UP = "🎭"
    THERAPY = "🛋️"
    RESEARCH = "🔬"
    BRAINSTORM = "💡"
    NEGOTIATION = "🤝"
    INTERVIEW = "🎤"
    STORYTELLING = "📚"
    TEACHING = "👨‍🏫"
    CONSULTING = "💼"
    DEFAULT = "🤖"

    # UI emojis
    FOLDER = "📁"
    HELP = "📚"
    STATUS = "📊"
    SETTINGS = "⚙️"


class Limits:
    """Configuration limits and constraints."""

    # Message limits
    MAX_TOPIC_LENGTH = 500
    MIN_TOPIC_LENGTH = 3
    MAX_MESSAGE_LENGTH = 2000
    MIN_MESSAGE_LENGTH = 1

    # ID limits
    MAX_PRESET_ID_LENGTH = 50
    MIN_PRESET_ID_LENGTH = 3
    MAX_USER_ID_LENGTH = 15
    MIN_USER_ID_LENGTH = 5

    # Conversation limits
    MAX_CONVERSATIONS_PER_USER = 3
    MESSAGE_RATE_LIMIT = 10
    CONVERSATION_TIMEOUT = 3600  # 1 hour
    USER_INPUT_TIMEOUT = 300  # 5 minutes

    # Display limits
    MAX_PRESETS_PER_ROW = 2
    MAX_EXAMPLES_DISPLAY = 3
    MAX_PRESET_DESCRIPTION_LENGTH = 200


class RegexPatterns:
    """Regular expression patterns for validation."""

    # Topic validation
    TOPIC_VALID_CHARS = r"^[a-zA-Z0-9\s\.,!?\-_()\']+$"

    # Preset ID validation
    PRESET_ID_VALID = r"^[a-zA-Z0-9_-]+$"

    # User ID validation
    USER_ID_VALID = r"^\d+$"

    # Conversation ID validation (UUID)
    CONVERSATION_ID_VALID = (
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )

    # Inappropriate content patterns
    INAPPROPRIATE_PATTERNS = [
        r"\b(spam|scam|phishing|malware|virus)\b",
        r"\b(hack|crack|exploit|breach)\b",
        r"\b(illegal|unlawful|criminal)\b",
        r"\b(hate|discrimination|racism|sexism)\b",
        r"\b(violence|threat|harm|kill|murder)\b",
        r"\b(drug|narcotic|addiction|overdose)\b",
        r"\b(terrorism|bomb|weapon|attack)\b",
    ]


class PresetCategories:
    """Preset categories for organization."""

    DISCUSSION = "Discussion"
    ENTERTAINMENT = "Entertainment"
    PROFESSIONAL = "Professional"
    EDUCATIONAL = "Educational"
    CREATIVE = "Creative"
    OTHER = "Other"


class DefaultValues:
    """Default values for various configurations."""

    # Preset defaults
    DEFAULT_PRESET_EMOJI = Emojis.DEFAULT
    DEFAULT_PRESET_CATEGORY = PresetCategories.OTHER
    DEFAULT_PRESET_DESCRIPTION = "A multi-agent conversation with AI agents."
    DEFAULT_EXAMPLE_TOPIC = "General discussion topic"

    # Conversation defaults
    DEFAULT_MAX_ROUNDS = 10
    DEFAULT_CONVERSATION_TIMEOUT = 3600

    # Display defaults
    DEFAULT_EXAMPLES_COUNT = 5
    DEFAULT_PRESET_DISPLAY_NAME = "Multi-Agent Conversation"


class Logging:
    """Logging configuration constants."""

    # Log levels
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    # Log formats
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )

    # Log files
    DEFAULT_LOG_FILE = "bot.log"
    ERROR_LOG_FILE = "bot_errors.log"
    ACCESS_LOG_FILE = "bot_access.log"


class Timeouts:
    """Timeout constants for various operations."""

    # Telegram API timeouts
    TELEGRAM_API_TIMEOUT = 30
    TELEGRAM_UPLOAD_TIMEOUT = 60

    # AgentryLab timeouts
    AGENTRYLAB_CONNECTION_TIMEOUT = 10
    AGENTRYLAB_RESPONSE_TIMEOUT = 30

    # Bot operation timeouts
    CONVERSATION_START_TIMEOUT = 60
    USER_INPUT_TIMEOUT = 300
    CONVERSATION_STREAM_TIMEOUT = 3600

    # Cleanup timeouts
    INACTIVE_USER_CLEANUP_HOURS = 24
    LOG_ROTATION_HOURS = 24
