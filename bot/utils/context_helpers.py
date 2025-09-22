"""
Context helper utilities for the Telegram bot.

This module provides utilities for accessing and validating context data,
reducing code duplication in handlers.
"""

from typing import Optional, Any, Union
from telegram import Update, Message, User, CallbackQuery
from telegram.ext import ContextTypes

from ..constants import Messages
from ..states.conversation import (
    ConversationStateManager,
    UserConversationState,
    ConversationState,
)
from ..utils.error_handling import (
    BotNotInitializedError,
    UserNotActiveError,
    ConversationNotFoundError,
)

# Global state manager instance
state_manager = ConversationStateManager()


def safe_get_message(update: Optional[Update]) -> Optional[Message]:
    """Safely get message from update."""
    return update.message if update else None


def safe_get_user(update: Optional[Update]) -> Optional[User]:
    """Safely get user from update."""
    if not update:
        return None
    if update.message and update.message.from_user:
        return update.message.from_user
    if update.callback_query and update.callback_query.from_user:
        return update.callback_query.from_user
    return None


def safe_get_callback_query(update: Optional[Update]) -> Optional[CallbackQuery]:
    """Safely get callback query from update."""
    return update.callback_query if update else None


def safe_get_user_id(update: Optional[Update]) -> Optional[str]:
    """Safely get user ID from update."""
    user = safe_get_user(update)
    return str(user.id) if user else None


def safe_get_message_text(message: Optional[Message]) -> Optional[str]:
    """Safely get text from message."""
    return message.text if message else None


def safe_get_callback_data(callback_query: Optional[CallbackQuery]) -> Optional[str]:
    """Safely get data from callback query."""
    return callback_query.data if callback_query else None


async def require_adapter_from_callback(
    callback_query: CallbackQuery, context: Optional[ContextTypes.DEFAULT_TYPE]
) -> Any:
    """
    Get adapter from context for callback queries.

    Args:
        callback_query: Telegram callback query object
        context: Bot context

    Returns:
        TelegramAdapter instance

    Raises:
        BotNotInitializedError: If adapter is not available
    """
    if context and hasattr(context, "bot_data") and context.bot_data is not None:
        adapter = context.bot_data.get("adapter")
        if adapter is not None:
            return adapter

    # Send error message to user
    await callback_query.edit_message_text(
        "❌ Bot is not properly initialized. Please try again later."
    )
    raise BotNotInitializedError("Adapter not available in context")


def set_user_data_from_callback(
    callback_query: CallbackQuery,
    context: Optional[ContextTypes.DEFAULT_TYPE],
    key: str,
    value: Any,
) -> None:
    """Set user data from callback query."""
    user_id = safe_get_user_id(Update(update_id=0, callback_query=callback_query))
    if user_id:
        set_user_data(
            Update(update_id=0, callback_query=callback_query), context, key, value
        )


def get_user_id_from_callback(callback_query: CallbackQuery) -> Optional[str]:
    """Get user ID from callback query."""
    return safe_get_user_id(Update(update_id=0, callback_query=callback_query))


def set_user_waiting_for_topic_from_callback(
    callback_query: CallbackQuery,
    context: Optional[ContextTypes.DEFAULT_TYPE],
    waiting: bool,
) -> None:
    """Set user waiting for topic from callback query."""
    if context is None:
        return
    set_user_waiting_for_topic(
        Update(update_id=0, callback_query=callback_query), context, waiting
    )


def clear_user_data_from_callback(
    callback_query: CallbackQuery, context: Optional[ContextTypes.DEFAULT_TYPE]
) -> None:
    """Clear user data from callback query."""
    clear_user_data(Update(update_id=0, callback_query=callback_query), context)


def get_adapter(context: Optional[ContextTypes.DEFAULT_TYPE]) -> Any:
    """
    Get adapter from context with validation.

    Args:
        context: Bot context

    Returns:
        TelegramAdapter instance

    Raises:
        BotNotInitializedError: If adapter is not available
    """
    if not context or not hasattr(context, "bot_data") or context.bot_data is None:
        raise BotNotInitializedError("Bot not properly initialized")

    adapter = context.bot_data.get("adapter")
    if not adapter:
        raise BotNotInitializedError("Bot not properly initialized")
    return adapter


async def require_adapter(
    update: Optional[Update], context: Optional[ContextTypes.DEFAULT_TYPE]
) -> Any:
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
        message = safe_get_message(update)
        if message:
            await message.reply_text(Messages.BOT_NOT_INITIALIZED)
        raise


def get_state_manager(
    context: Optional[ContextTypes.DEFAULT_TYPE],
) -> ConversationStateManager:
    """
    Get state manager from context with validation.

    Args:
        context: Bot context

    Returns:
        ConversationStateManager instance

    Raises:
        BotNotInitializedError: If state manager is not available
    """
    if context and hasattr(context, "bot_data") and context.bot_data is not None:
        state_mgr = context.bot_data.get("state_manager")
        if state_mgr:
            return state_mgr

    # Fallback to registry state manager if available
    try:
        from ..services import services  # Local import to avoid circular dependency

        if services.state_manager:
            return services.state_manager
    except Exception:  # nosec B110 - defensive fallback for circular import
        # This is a defensive fallback when services module is not available
        # Log the exception for debugging but continue with fallback
        import logging
        logger = logging.getLogger(__name__)
        logger.debug("Services module not available, using fallback state manager", exc_info=True)

    return state_manager


def get_user_id(update: Optional[Update]) -> Optional[str]:
    """
    Extract user ID from update.

    Args:
        update: Telegram update object

    Returns:
        User ID as string
    """
    return safe_get_user_id(update)


def get_user_state(
    update: Optional[Update], context: Optional[ContextTypes.DEFAULT_TYPE]
) -> UserConversationState:
    """
    Get user conversation state.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        UserConversationState instance
    """
    user_id = get_user_id(update)
    if user_id is None:
        raise UserNotActiveError("User information not available")

    state_mgr = get_state_manager(context)
    return state_mgr.get_user_state(user_id)


async def require_active_user(
    update: Optional[Update], context: Optional[ContextTypes.DEFAULT_TYPE]
) -> UserConversationState:
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
        message = safe_get_message(update)
        if message:
            await message.reply_text(Messages.NO_ACTIVE_CONVERSATION)
        raise UserNotActiveError("User has no active conversation")

    return user_state


async def require_user_in_conversation(
    update: Optional[Update], context: Optional[ContextTypes.DEFAULT_TYPE]
) -> UserConversationState:
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
        message = safe_get_message(update)
        if message:
            await message.reply_text(Messages.NO_ACTIVE_CONVERSATION)
        raise UserNotActiveError("User is not in conversation")

    return user_state


async def require_paused_conversation(
    update: Optional[Update], context: Optional[ContextTypes.DEFAULT_TYPE]
) -> UserConversationState:
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
        message = safe_get_message(update)
        if message:
            await message.reply_text(Messages.NO_PAUSED_CONVERSATION)
        raise UserNotActiveError("User has no paused conversation")

    return user_state


def get_conversation_id(
    update: Optional[Update], context: Optional[ContextTypes.DEFAULT_TYPE]
) -> str:
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


async def require_conversation_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
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
        message = safe_get_message(update)
        if message:
            await message.reply_text(Messages.NO_CONVERSATION_FOUND)
        raise


def get_user_data(
    update: Optional[Update],
    context: Optional[ContextTypes.DEFAULT_TYPE],
    key: str,
    default: Any = None,
) -> Any:
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
    if not context or not hasattr(context, "user_data") or context.user_data is None:
        return default
    return context.user_data.get(key, default)


def set_user_data(
    update: Optional[Update],
    context: Optional[ContextTypes.DEFAULT_TYPE],
    key: str,
    value: Any,
) -> None:
    """
    Set user data in context.

    Args:
        update: Telegram update object
        context: Bot context
        key: Data key
        value: Data value
    """
    if not context or not hasattr(context, "user_data") or context.user_data is None:
        return
    context.user_data[key] = value


def clear_user_data(
    update: Optional[Update], context: Optional[ContextTypes.DEFAULT_TYPE], *keys: str
) -> None:
    """
    Clear user data from context.

    Args:
        update: Telegram update object
        context: Bot context
        *keys: Keys to clear (if none provided, clears all)
    """
    if not context or not hasattr(context, "user_data") or context.user_data is None:
        return

    if keys:
        for key in keys:
            context.user_data.pop(key, None)
    else:
        context.user_data.clear()


def get_bot_data(
    context: Optional[ContextTypes.DEFAULT_TYPE], key: str, default: Any = None
) -> Any:
    """
    Get bot data from context.

    Args:
        context: Bot context
        key: Data key
        default: Default value if key not found

    Returns:
        Bot data value
    """
    if not context or not hasattr(context, "bot_data") or context.bot_data is None:
        return default
    return context.bot_data.get(key, default)


def set_bot_data(
    context: Optional[ContextTypes.DEFAULT_TYPE], key: str, value: Any
) -> None:
    """
    Set bot data in context.

    Args:
        context: Bot context
        key: Data key
        value: Data value
    """
    if not context or not hasattr(context, "bot_data") or context.bot_data is None:
        return
    context.bot_data[key] = value


def is_user_waiting_for_topic(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """
    Check if user is waiting for topic input.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        True if user is waiting for topic input
    """
    return get_user_data(update, context, "waiting_for_topic", False)


def set_user_waiting_for_topic(
    update: Update, context: ContextTypes.DEFAULT_TYPE, waiting: bool = True
) -> None:
    """
    Set user waiting for topic input state.

    Args:
        update: Telegram update object
        context: Bot context
        waiting: Whether user is waiting for topic input
    """
    set_user_data(update, context, "waiting_for_topic", waiting)


def get_selected_preset(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[str]:
    """
    Get selected preset from user data.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Selected preset ID or None
    """
    return get_user_data(update, context, "selected_preset")


def set_selected_preset(
    update: Update, context: ContextTypes.DEFAULT_TYPE, preset_id: str
) -> None:
    """
    Set selected preset in user data.

    Args:
        update: Telegram update object
        context: Bot context
        preset_id: Preset ID to set
    """
    set_user_data(update, context, "selected_preset", preset_id)


def get_selected_topic(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[str]:
    """
    Get selected topic from user data.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Selected topic or None
    """
    return get_user_data(update, context, "selected_topic")


def set_selected_topic(
    update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str
) -> None:
    """
    Set selected topic in user data.

    Args:
        update: Telegram update object
        context: Bot context
        topic: Topic to set
    """
    set_user_data(update, context, "selected_topic", topic)


def clear_conversation_data(
    update: Optional[Update], context: Optional[ContextTypes.DEFAULT_TYPE]
) -> None:
    """
    Clear conversation-related user data.

    Args:
        update: Telegram update object
        context: Bot context
    """
    clear_user_data(
        update, context, "waiting_for_topic", "selected_preset", "selected_topic"
    )


def get_message_text(update: Optional[Update]) -> str:
    """
    Get message text from update.

    Args:
        update: Telegram update object

    Returns:
        Message text
    """
    message = safe_get_message(update)
    if message and message.text:
        return message.text.strip()

    callback_query = safe_get_callback_query(update)
    if callback_query and callback_query.data:
        return callback_query.data
    else:
        return ""


def get_callback_data(update: Optional[Update]) -> Optional[str]:
    """
    Get callback data from update.

    Args:
        update: Telegram update object

    Returns:
        Callback data or None
    """
    callback_query = safe_get_callback_query(update)
    if callback_query:
        return callback_query.data
    return None


def is_callback_query(update: Optional[Update]) -> bool:
    """
    Check if update is a callback query.

    Args:
        update: Telegram update object

    Returns:
        True if update is a callback query
    """
    return bool(update and getattr(update, "callback_query", None))


def is_text_message(update: Optional[Update]) -> bool:
    """
    Check if update is a text message.

    Args:
        update: Telegram update object

    Returns:
        True if update is a text message
    """
    message = safe_get_message(update)
    return bool(message and message.text is not None)


def get_user_info(update: Optional[Update]) -> Optional[dict]:
    """
    Get user information from update.

    Args:
        update: Telegram update object

    Returns:
        Dictionary with user information
    """
    user = safe_get_user(update)
    if not user:
        return None
    return {
        "id": user.id,
        "username": getattr(user, "username", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "full_name": f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip()
        or None,
    }
