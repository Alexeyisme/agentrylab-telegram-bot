"""Command handlers exposed to Telegram application and tests."""

from __future__ import annotations

import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from ..config import HELP_MSG, NO_CONVERSATION_MSG, WELCOME_MSG
from ..services import services
from ..states.conversation import ConversationState
from ..keyboards.reply import create_main_menu_keyboard
from ..utils.context_helpers import (
    clear_user_data,
    get_state_manager,
    require_adapter,
    set_user_waiting_for_topic,
)
from . import conversation as conversation_handlers
from . import presets as preset_handlers

logger = logging.getLogger(__name__)


def _resolve_state_manager(context: Optional[ContextTypes.DEFAULT_TYPE]):
    """Return the most appropriate ConversationStateManager."""
    if context is not None:
        try:
            return get_state_manager(context)
        except Exception as exc:  # pragma: no cover - only for defensive logging
            logger.debug("Could not retrieve state manager from context: %s", exc)
    return services.state_manager


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    if not user:
        return
    
    user_id = str(user.id)
    user_name = user.first_name or user.username or "there"

    state_manager = _resolve_state_manager(context)
    state_manager.reset_user_state(user_id)
    state_manager.set_user_state(user_id, ConversationState.SELECTING_PRESET)
    clear_user_data(update, context)
    set_user_waiting_for_topic(update, context, False)

    message = update.message
    if not message:
        return
    
    await message.reply_text(
        WELCOME_MSG.format(name=user_name),
        parse_mode="Markdown",
        reply_markup=create_main_menu_keyboard()
    )

    await preset_handlers.show_presets(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    message = update.message
    if not message:
        return
    
    await message.reply_text(
        HELP_MSG, 
        parse_mode="Markdown",
        reply_markup=create_main_menu_keyboard()
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command."""
    user = update.effective_user
    if not user:
        return
    
    user_id = str(user.id)
    state_manager = _resolve_state_manager(context)
    user_state = state_manager.get_user_state(user_id)

    message = update.message
    if not message:
        return

    if not state_manager.is_user_active(user_id):
        await message.reply_text(NO_CONVERSATION_MSG)
        return

    state_value = (
        user_state.state.value
        if isinstance(user_state.state, ConversationState)
        else str(user_state.state)
    )

    lines = [
        "📊 **Your Conversation Status:**",
        "",
        f"**State:** {state_value}",
        f"**Preset:** {user_state.selected_preset or '—'}",
        f"**Topic:** {user_state.selected_topic or '—'}",
    ]
    if user_state.conversation_id:
        lines.append(f"**Conversation ID:** {user_state.conversation_id}")

    await message.reply_text("\n".join(lines), parse_mode="Markdown")


async def presets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /presets command."""
    try:
        await preset_handlers.show_presets(update, context)
    except Exception as exc:  # pragma: no cover - network/adapter failures
        logger.error("Error retrieving presets: %s", exc)
        message = update.message
        if not message:
            return
        
        await message.reply_text("❌ Error retrieving presets. Please try again.")


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /pause command."""
    await conversation_handlers.pause_conversation(update, context)


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /resume command."""
    await conversation_handlers.resume_conversation(update, context)


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stop command."""
    await conversation_handlers.stop_conversation(update, context)


# Backwards compatibility ----------------------------------------------------

async def show_presets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Legacy wrapper retained for older imports/tests."""
    await presets_command(update, context)


presets_show_presets = presets_command
