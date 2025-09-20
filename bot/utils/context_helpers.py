"""
Context helper utilities for the Telegram bot.

This module provides utilities for accessing and validating context data,
reducing code duplication in handlers.
"""

from typing import Optional, Any
from telegram import Update
from telegram.ext import ContextTypes

from ..constants import Messages
from ..states.conversation import ConversationStateManager, UserConversationState, ConversationState
from ..utils.error_handling import BotNotInitializedError, UserNotActiveError, ConversationNotFoundError

# Global state manager instance
state_manager = ConversationStateManager()


def get_adapter(context: ContextTypes.DEFAULT_TYPE) -> Any:
    """
    Get adapter from context with validation.
    
    Args:
        context: Bot context
        
    Returns:
        TelegramAdapter instance
        
    Raises:
        BotNotInitializedError: If adapter is not available
    """
    adapter = context.bot_data.get('adapter')
    if not adapter:
        raise BotNotInitializedError("Bot not properly initialized")
    return adapter


async def require_adapter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Any:
    """
    Get adapter from context or send error message if not available.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        TelegramAdapter instance
        
    Raises:
        BotNotInitializedError: If adapter is not available
    """
    try:
        return get_adapter(context)
    except BotNotInitializedError:
        await update.message.reply_text(Messages.BOT_NOT_INITIALIZED)
        raise


def get_state_manager(context: ContextTypes.DEFAULT_TYPE) -> ConversationStateManager:
    """
    Get state manager from context with validation.
    
    Args:
        context: Bot context
        
    Returns:
        ConversationStateManager instance
        
    Raises:
        BotNotInitializedError: If state manager is not available
    """
    state_mgr = context.bot_data.get('state_manager')
    if not state_mgr:
        # Fallback to global instance
        return state_manager
    return state_mgr


def get_user_id(update: Update) -> str:
    """
    Extract user ID from update.
    
    Args:
        update: Telegram update object
        
    Returns:
        User ID as string
    """
    if update.effective_user:
        return str(update.effective_user.id)
    elif update.callback_query and update.callback_query.from_user:
        return str(update.callback_query.from_user.id)
    else:
        raise ValueError("Could not extract user ID from update")


def get_user_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> UserConversationState:
    """
    Get user conversation state.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        UserConversationState instance
    """
    user_id = get_user_id(update)
    state_mgr = get_state_manager(context)
    return state_mgr.get_user_state(user_id)


async def require_active_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> UserConversationState:
    """
    Get user state or send error message if not active.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        UserConversationState instance
        
    Raises:
        UserNotActiveError: If user has no active conversation
    """
    user_state = get_user_state(update, context)
    
    if not user_state.is_active():
        await update.message.reply_text(Messages.NO_ACTIVE_CONVERSATION)
        raise UserNotActiveError("User has no active conversation")
    
    return user_state


async def require_user_in_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> UserConversationState:
    """
    Get user state or send error message if not in conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        UserConversationState instance
        
    Raises:
        UserNotActiveError: If user is not in conversation
    """
    user_state = get_user_state(update, context)
    
    if not user_state.is_in_conversation():
        await update.message.reply_text(Messages.NO_ACTIVE_CONVERSATION)
        raise UserNotActiveError("User is not in conversation")
    
    return user_state


async def require_paused_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> UserConversationState:
    """
    Get user state or send error message if no paused conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        UserConversationState instance
        
    Raises:
        UserNotActiveError: If user has no paused conversation
    """
    user_state = get_user_state(update, context)
    
    if user_state.state != ConversationState.CONVERSATION_PAUSED:
        await update.message.reply_text(Messages.NO_PAUSED_CONVERSATION)
        raise UserNotActiveError("User has no paused conversation")
    
    return user_state


def get_conversation_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Get conversation ID from user state.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        Conversation ID
        
    Raises:
        ConversationNotFoundError: If no conversation ID found
    """
    user_state = get_user_state(update, context)
    
    if not user_state.conversation_id:
        raise ConversationNotFoundError("No conversation ID found")
    
    return user_state.conversation_id


async def require_conversation_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Get conversation ID or send error message if not found.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        Conversation ID
        
    Raises:
        ConversationNotFoundError: If no conversation ID found
    """
    try:
        return get_conversation_id(update, context)
    except ConversationNotFoundError:
        await update.message.reply_text(Messages.NO_CONVERSATION_FOUND)
        raise


def get_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, default: Any = None) -> Any:
    """
    Get user data from context.
    
    Args:
        update: Telegram update object
        context: Bot context
        key: Data key
        default: Default value if key not found
        
    Returns:
        User data value
    """
    return context.user_data.get(key, default)


def set_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, value: Any) -> None:
    """
    Set user data in context.
    
    Args:
        update: Telegram update object
        context: Bot context
        key: Data key
        value: Data value
    """
    context.user_data[key] = value


def clear_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE, *keys: str) -> None:
    """
    Clear user data from context.
    
    Args:
        update: Telegram update object
        context: Bot context
        *keys: Keys to clear (if none provided, clears all)
    """
    if keys:
        for key in keys:
            context.user_data.pop(key, None)
    else:
        context.user_data.clear()


def get_bot_data(context: ContextTypes.DEFAULT_TYPE, key: str, default: Any = None) -> Any:
    """
    Get bot data from context.
    
    Args:
        context: Bot context
        key: Data key
        default: Default value if key not found
        
    Returns:
        Bot data value
    """
    return context.bot_data.get(key, default)


def set_bot_data(context: ContextTypes.DEFAULT_TYPE, key: str, value: Any) -> None:
    """
    Set bot data in context.
    
    Args:
        context: Bot context
        key: Data key
        value: Data value
    """
    context.bot_data[key] = value


def is_user_waiting_for_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user is waiting for topic input.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        True if user is waiting for topic input
    """
    return get_user_data(update, context, 'waiting_for_topic', False)


def set_user_waiting_for_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, waiting: bool = True) -> None:
    """
    Set user waiting for topic input state.
    
    Args:
        update: Telegram update object
        context: Bot context
        waiting: Whether user is waiting for topic input
    """
    set_user_data(update, context, 'waiting_for_topic', waiting)


def get_selected_preset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """
    Get selected preset from user data.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        Selected preset ID or None
    """
    return get_user_data(update, context, 'selected_preset')


def set_selected_preset(update: Update, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Set selected preset in user data.
    
    Args:
        update: Telegram update object
        context: Bot context
        preset_id: Preset ID to set
    """
    set_user_data(update, context, 'selected_preset', preset_id)


def get_selected_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """
    Get selected topic from user data.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        Selected topic or None
    """
    return get_user_data(update, context, 'selected_topic')


def set_selected_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str) -> None:
    """
    Set selected topic in user data.
    
    Args:
        update: Telegram update object
        context: Bot context
        topic: Topic to set
    """
    set_user_data(update, context, 'selected_topic', topic)


def clear_conversation_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Clear conversation-related user data.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    clear_user_data(update, context, 'waiting_for_topic', 'selected_preset', 'selected_topic')


def get_message_text(update: Update) -> str:
    """
    Get message text from update.
    
    Args:
        update: Telegram update object
        
    Returns:
        Message text
    """
    if update.message and update.message.text:
        return update.message.text.strip()
    elif update.callback_query and update.callback_query.data:
        return update.callback_query.data
    else:
        return ""


def get_callback_data(update: Update) -> Optional[str]:
    """
    Get callback data from update.
    
    Args:
        update: Telegram update object
        
    Returns:
        Callback data or None
    """
    if update.callback_query:
        return update.callback_query.data
    return None


def is_callback_query(update: Update) -> bool:
    """
    Check if update is a callback query.
    
    Args:
        update: Telegram update object
        
    Returns:
        True if update is a callback query
    """
    return update.callback_query is not None


def is_text_message(update: Update) -> bool:
    """
    Check if update is a text message.
    
    Args:
        update: Telegram update object
        
    Returns:
        True if update is a text message
    """
    return update.message is not None and update.message.text is not None


def get_user_info(update: Update) -> dict:
    """
    Get user information from update.
    
    Args:
        update: Telegram update object
        
    Returns:
        Dictionary with user information
    """
    user = update.effective_user
    if not user:
        return {}
    
    return {
        'id': str(user.id),
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip()
    }
