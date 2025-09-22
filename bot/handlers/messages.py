"""Message routing helpers that delegate to conversation handlers."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from ..keyboards.reply import (
    is_keyboard_button, 
    get_command_from_button,
    create_main_menu_keyboard
)
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

    # Check if it's a keyboard button press first
    message = update.message
    if not message or not message.text:
        return
    
    message_text = message.text.strip()
    if is_keyboard_button(message_text):
        command = get_command_from_button(message_text)
        if command:
            await handle_keyboard_command(update, context, command)
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


async def handle_keyboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> None:
    """Handle commands triggered by keyboard buttons."""
    # Import command handlers
    from . import commands
    
    # Route to appropriate command handler
    if command == "/start":
        await commands.start_command(update, context)
    elif command == "/help":
        await commands.help_command(update, context)
    elif command == "/status":
        await commands.status_command(update, context)
    elif command == "/presets":
        await commands.presets_command(update, context)
    elif command == "/pause":
        await commands.pause_command(update, context)
    elif command == "/resume":
        await commands.resume_command(update, context)
    elif command == "/stop":
        await commands.stop_command(update, context)
