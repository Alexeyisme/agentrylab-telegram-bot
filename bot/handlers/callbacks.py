"""
Simplified callback handlers.
"""

import logging
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from ..config import (
    PREFIX_SELECT,
    PREFIX_INFO,
    PREFIX_EXAMPLES,
    PREFIX_CUSTOM,
    PREFIX_CONFIRM,
)
from ..services import services
from ..constants import ConversationStates
from ..utils.context_helpers import get_state_manager

logger = logging.getLogger(__name__)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries."""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data
    if not data:
        return

    user = query.from_user
    if not user:
        return

    user_id = str(user.id)

    try:
        if data.startswith(PREFIX_SELECT):
            await handle_preset_selection(query, context, data)
        elif data.startswith(PREFIX_INFO):
            await handle_preset_info(query, context, data)
        elif data.startswith(PREFIX_EXAMPLES):
            await handle_preset_examples(query, context, data)
        elif data.startswith(PREFIX_CUSTOM):
            await handle_custom_topic(query, context, data)
        elif data.startswith(PREFIX_CONFIRM):
            await handle_topic_confirmation(query, context, data)
        else:
            await query.edit_message_text("❌ Unknown action. Please try again.")

    except Exception as e:
        logger.error(f"Error handling callback: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")


async def handle_preset_selection(
    query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str
) -> None:
    """Handle preset selection."""
    preset_id = data.replace(PREFIX_SELECT, "")
    user_id = str(query.from_user.id)

    # Store selected preset
    state_manager = get_state_manager(context)
    state_manager.set_user_preset(user_id, preset_id)
    state_manager.set_user_state(user_id, ConversationStates.ENTERING_TOPIC)

    # Ask for topic
    await query.edit_message_text(
        f"📝 **Enter a topic for your conversation:**\n\n"
        f"Preset: {preset_id}\n\n"
        f"Type your topic below:",
        parse_mode="Markdown",
    )


async def handle_preset_info(
    query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str
) -> None:
    """Handle preset info request."""
    preset_id = data.replace(PREFIX_INFO, "")

    try:
        preset_service = services.get_preset_service()
        preset_info = await preset_service.get_preset_info(preset_id)

        info_text = f"📋 **{preset_id}**\n\n"
        info_text += f"**Description:** {preset_info.get('description', 'No description available')}\n\n"
        info_text += (
            f"**Examples:** {preset_info.get('examples', 'No examples available')}"
        )

        await query.edit_message_text(info_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error getting preset info: {e}")
        await query.edit_message_text("❌ Error loading preset info.")


async def handle_preset_examples(
    query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str
) -> None:
    """Handle preset examples request."""
    preset_id = data.replace(PREFIX_EXAMPLES, "")

    try:
        preset_service = services.get_preset_service()
        examples = await preset_service.get_preset_examples(preset_id)

        examples_text = f"💡 **Examples for {preset_id}:**\n\n"
        for i, example in enumerate(examples[:3], 1):
            examples_text += f"{i}. {example}\n"

        await query.edit_message_text(examples_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error getting preset examples: {e}")
        await query.edit_message_text("❌ Error loading examples.")


async def handle_custom_topic(
    query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str
) -> None:
    """Handle custom topic input."""
    preset_id = data.replace(PREFIX_CUSTOM, "")
    user_id = str(query.from_user.id)

    # Store selected preset
    state_manager = get_state_manager(context)
    state_manager.set_user_preset(user_id, preset_id)
    state_manager.set_user_state(user_id, ConversationStates.ENTERING_TOPIC)

    # Ask for topic
    await query.edit_message_text(
        f"📝 **Enter a custom topic:**\n\n"
        f"Preset: {preset_id}\n\n"
        f"Type your topic below:",
        parse_mode="Markdown",
    )


async def handle_topic_confirmation(
    query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str
) -> None:
    """Handle topic confirmation."""
    # Extract preset_id and topic from data
    parts = data.replace(PREFIX_CONFIRM, "").split("|")
    if len(parts) != 2:
        await query.edit_message_text("❌ Invalid confirmation data.")
        return

    preset_id, topic = parts
    user_id = str(query.from_user.id)

    # Start conversation
    try:
        state_manager = get_state_manager(context)
        conversation_service = services.get_conversation_service()
        conversation_id = await conversation_service.start_conversation(
            user_id, preset_id, topic
        )

        # Update user state
        state_manager.set_user_conversation_id(user_id, conversation_id)
        state_manager.set_user_state(user_id, ConversationStates.IN_CONVERSATION)

        await query.edit_message_text(
            f"🚀 **Conversation Started!**\n\n"
            f"Preset: {preset_id}\n"
            f"Topic: {topic}\n\n"
            f"Watch the agents interact in real-time!",
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await query.edit_message_text(
            "❌ Error starting conversation. Please try again."
        )


async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Legacy wrapper that forwards to preset handlers."""
    from . import presets as preset_handlers

    if update and update.callback_query and update.callback_query.data:
        await handle_callback(update, context)
    else:
        await preset_handlers.handle_preset_callback(update, context)
