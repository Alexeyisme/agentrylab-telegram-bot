"""Message routing helpers that delegate to conversation handlers."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from ..states.conversation import ConversationState
from ..utils.context_helpers import (
    get_state_manager,
    get_user_id,
    is_user_waiting_for_topic,
)
from . import conversation as conversation_handlers


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dispatch incoming messages to the appropriate conversation handler."""
    user_id = get_user_id(update)
    if user_id is None:
        return

    state_manager = get_state_manager(context)
    user_state = state_manager.get_user_state(user_id)

    if is_user_waiting_for_topic(update, context) or user_state.state in {
        ConversationState.SELECTING_PRESET,
        ConversationState.ENTERING_TOPIC,
        ConversationState.CONFIRMING_TOPIC,
    }:
        await conversation_handlers.handle_topic_input(update, context)
        return

    if user_state.state in {
        ConversationState.IN_CONVERSATION,
        ConversationState.WAITING_FOR_USER_INPUT,
        ConversationState.CONVERSATION_PAUSED,
    }:
        await conversation_handlers.handle_conversation_input(update, context)
    else:
        await conversation_handlers.handle_regular_message(update, context)
