"""
Persistent reply keyboards for the Telegram bot.
These keyboards are always visible on screen and provide quick access to commands.
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional


def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Create the main persistent keyboard that's always visible.
    
    Returns:
        ReplyKeyboardMarkup with main command buttons
    """
    keyboard = [
        [
            KeyboardButton("🚀 Start New"),
            KeyboardButton("🎭 Presets"),
            KeyboardButton("📊 Status")
        ],
        [
            KeyboardButton("⏸️ Pause"),
            KeyboardButton("▶️ Resume"),
            KeyboardButton("⏹️ Stop")
        ],
        [
            KeyboardButton("❓ Help"),
            KeyboardButton("ℹ️ About")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,  # Keep keyboard persistent
        input_field_placeholder="Type a message or use buttons above..."
    )


def create_conversation_control_keyboard() -> ReplyKeyboardMarkup:
    """
    Create a keyboard specifically for conversation control.
    Use this when user is in an active conversation.
    
    Returns:
        ReplyKeyboardMarkup with conversation control buttons
    """
    keyboard = [
        [
            KeyboardButton("⏸️ Pause"),
            KeyboardButton("▶️ Resume"),
            KeyboardButton("⏹️ Stop")
        ],
        [
            KeyboardButton("📊 Status"),
            KeyboardButton("🎭 New Preset")
        ],
        [
            KeyboardButton("❓ Help")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Type your message or use controls above..."
    )


def create_preset_selection_keyboard() -> ReplyKeyboardMarkup:
    """
    Create a keyboard for preset selection.
    
    Returns:
        ReplyKeyboardMarkup with preset selection buttons
    """
    keyboard = [
        [
            KeyboardButton("🎭 Debates"),
            KeyboardButton("🎪 Stand-up")
        ],
        [
            KeyboardButton("🛋️ Therapy"),
            KeyboardButton("🔬 Research")
        ],
        [
            KeyboardButton("💡 Brainstorm"),
            KeyboardButton("🤝 Negotiation")
        ],
        [
            KeyboardButton("🎤 Interview"),
            KeyboardButton("📚 Storytelling")
        ],
        [
            KeyboardButton("👨‍🏫 Teaching"),
            KeyboardButton("💼 Consulting")
        ],
        [
            KeyboardButton("🔙 Back to Main"),
            KeyboardButton("❓ Help")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Select a conversation type..."
    )


def create_simple_keyboard() -> ReplyKeyboardMarkup:
    """
    Create a simple keyboard with basic commands.
    Use this as a fallback or for minimal interface.
    
    Returns:
        ReplyKeyboardMarkup with basic buttons
    """
    keyboard = [
        [
            KeyboardButton("🚀 Start"),
            KeyboardButton("❓ Help")
        ],
        [
            KeyboardButton("📊 Status")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Type a message..."
    )


def remove_keyboard() -> ReplyKeyboardMarkup:
    """
    Remove the persistent keyboard.
    
    Returns:
        ReplyKeyboardMarkup that removes the keyboard
    """
    return ReplyKeyboardMarkup(
        [[]],
        resize_keyboard=True,
        one_time_keyboard=True,
        remove_keyboard=True
    )


def get_keyboard_for_state(state: str) -> ReplyKeyboardMarkup:
    """
    Get the appropriate keyboard based on user state.
    
    Args:
        state: Current user state
        
    Returns:
        Appropriate ReplyKeyboardMarkup
    """
    if state == "in_conversation":
        return create_conversation_control_keyboard()
    elif state == "selecting_preset":
        return create_preset_selection_keyboard()
    elif state == "entering_topic":
        return create_simple_keyboard()
    else:
        return create_main_menu_keyboard()


def is_keyboard_button(text: str) -> bool:
    """
    Check if the text corresponds to a keyboard button.
    
    Args:
        text: Message text to check
        
    Returns:
        True if text is a keyboard button
    """
    keyboard_buttons = {
        "🚀 Start New", "🎭 Presets", "📊 Status", "⏸️ Pause", "▶️ Resume", "⏹️ Stop",
        "❓ Help", "ℹ️ About", "🎭 Debates", "🎪 Stand-up", "🛋️ Therapy", "🔬 Research",
        "💡 Brainstorm", "🤝 Negotiation", "🎤 Interview", "📚 Storytelling", 
        "👨‍🏫 Teaching", "💼 Consulting", "🔙 Back to Main", "🎭 New Preset", "🚀 Start"
    }
    
    return text in keyboard_buttons


def get_command_from_button(button_text: str) -> Optional[str]:
    """
    Convert keyboard button text to corresponding command.
    
    Args:
        button_text: The button text
        
    Returns:
        Corresponding command or None
    """
    button_to_command = {
        "🚀 Start New": "/start",
        "🎭 Presets": "/presets", 
        "📊 Status": "/status",
        "⏸️ Pause": "/pause",
        "▶️ Resume": "/resume",
        "⏹️ Stop": "/stop",
        "❓ Help": "/help",
        "ℹ️ About": "/help",
        "🔙 Back to Main": "/start",
        "🎭 New Preset": "/presets",
        "🚀 Start": "/start"
    }
    
    return button_to_command.get(button_text)
