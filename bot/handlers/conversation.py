"""
Conversation management handlers for the Telegram bot.
"""

import logging
import asyncio
from typing import Optional

from telegram import Update, Message
from telegram.ext import ContextTypes

from ..constants import Messages, ConversationStates
from ..keyboards.presets import create_topic_confirmation_keyboard
from ..keyboards.reply import create_main_menu_keyboard
from ..services.conversation_service import ConversationService
from ..services.preset_service import PresetService
from ..states.conversation import ConversationState
from ..templates.messages import MessageTemplates
from ..utils.context_helpers import (
    get_user_id,
    get_user_data,
    set_user_data,
    clear_user_data,
    is_user_waiting_for_topic,
    get_selected_preset,
    get_selected_topic,
    get_state_manager,
)
from ..utils.error_handling import handle_errors
from ..utils.validation import validate_topic_input

logger = logging.getLogger(__name__)

@handle_errors("Error processing your topic. Please try again.")
async def handle_topic_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle topic input from users.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = get_user_id(update)
    state_manager = get_state_manager(context)
    message_text = update.message.text.strip()
    
    # Check if user is waiting for topic input using new utility
    user_state = state_manager.get_user_state(user_id)
    waiting_for_topic = is_user_waiting_for_topic(update, context)
    expecting_topic = user_state.state in {
        ConversationState.SELECTING_PRESET,
        ConversationState.ENTERING_TOPIC,
        ConversationState.CONFIRMING_TOPIC,
    }

    if not waiting_for_topic and not expecting_topic:
        # User is not in topic input mode, handle as regular message
        await handle_regular_message(update, context)
        return

    # Validate topic input
    validation_result = validate_topic_input(message_text)
    if not validation_result['valid']:
        error_message = MessageTemplates.topic_validation_error(validation_result.get('error_type', 'general'))
        await update.message.reply_text(
            f"❌ {error_message}\n\n"
            "Please enter a valid topic. For example:\n"
            "• Should remote work become the standard?\n"
            "• How to improve team productivity?\n"
            "• The future of artificial intelligence"
        )
        return
    
    # Get selected preset using new utility
    preset_id = get_selected_preset(update, context)
    if not preset_id:
        await update.message.reply_text(Messages.NO_PRESET_SELECTED)
        return
    
    # Store topic using new utility
    set_user_data(update, context, 'selected_topic', message_text)
    
    # Get adapter and create services
    from ..utils.context_helpers import require_adapter
    adapter = await require_adapter(update, context)
    preset_service = PresetService(adapter)
    
    # Get preset information using service
    preset_info = await preset_service.get_preset_info(preset_id)
    
    # Create confirmation message using template
    message = MessageTemplates.topic_confirmation_message(
        emoji=preset_info['emoji'],
        display_name=preset_info['display_name'],
        topic=message_text
    )
    
    keyboard = create_topic_confirmation_keyboard(preset_id, message_text)
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    
    # Clear waiting state using new utility
    set_user_data(update, context, 'waiting_for_topic', False)

    # Update user state
    state_manager.set_user_state(user_id, ConversationState.CONFIRMING_TOPIC)
    state_manager.set_user_preset(user_id, preset_id)
    state_manager.set_user_topic(user_id, message_text)


@handle_errors("Error processing your message. Please try again.")
async def handle_regular_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle regular messages from users.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = get_user_id(update)
    state_manager = get_state_manager(context)

    # Check if user is in a conversation
    if state_manager.is_user_in_conversation(user_id):
        # User is in conversation, handle as conversation input
        await handle_conversation_input(update, context)
        return
    
    # User is not in conversation, provide help using template
    await update.message.reply_text(
        MessageTemplates.regular_message_response(),
        parse_mode='Markdown',
        reply_markup=create_main_menu_keyboard()
    )


@handle_errors("Error processing your input. Please try again.")
async def handle_conversation_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle user input during an active conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = get_user_id(update)
    state_manager = get_state_manager(context)
    message_text = update.message.text.strip()
    
    # Get user state
    user_state = state_manager.get_user_state(user_id)
    
    # Check if user is waiting for input
    if user_state.state != ConversationState.WAITING_FOR_USER_INPUT:
        await update.message.reply_text(
            MessageTemplates.waiting_for_turn_message(),
            parse_mode='Markdown'
        )
        return
    
    # Get conversation ID
    conversation_id = user_state.conversation_id
    if not conversation_id:
        await update.message.reply_text(Messages.NO_CONVERSATION_FOUND)
        return
    
    # Get adapter and create conversation service
    from ..utils.context_helpers import require_adapter
    adapter = await require_adapter(update, context)
    conversation_service = ConversationService(adapter, state_manager)
    
    # Handle user input using service
    try:
        success = await conversation_service.handle_user_input(user_id, message_text)
        
        if success:
            # Show confirmation using template
            await update.message.reply_text(
                MessageTemplates.message_sent_message(),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                MessageTemplates.waiting_for_turn_message(),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error posting user message: {e}")
        await update.message.reply_text(
            "❌ Error sending your message. Please try again."
        )


@handle_errors("Error starting conversation. Please try again.")
async def start_conversation_with_agentrylab(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                           preset_id: str, topic: str) -> Optional[str]:
    """
    Start a conversation with AgentryLab.
    
    Args:
        update: Telegram update object
        context: Bot context
        preset_id: The preset ID
        topic: The topic text
        
    Returns:
        Conversation ID if successful, None otherwise
    """
    user_id = get_user_id(update)
    state_manager = get_state_manager(context)
    
    # Get adapter and create conversation service
    from ..utils.context_helpers import require_adapter
    adapter = await require_adapter(update, context)
    conversation_service = ConversationService(adapter, state_manager)
    
    # Start conversation using service
    conversation_id = await conversation_service.start_conversation(
        user_id=user_id,
        preset_id=preset_id,
        topic=topic,
        max_rounds=10
    )
    
    # Start conversation streaming task
    asyncio.create_task(stream_conversation_events(update, context, conversation_id))
    
    return conversation_id


async def stream_conversation_events(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   conversation_id: str) -> None:
    """
    Stream conversation events from AgentryLab.
    
    Args:
        update: Telegram update object
        context: Bot context
        conversation_id: The conversation ID
    """
    user_id = get_user_id(update)
    state_manager = get_state_manager(context)
    
    try:
        # Get adapter and create conversation service
        from ..utils.context_helpers import require_adapter
        adapter = await require_adapter(update, context)
        conversation_service = ConversationService(adapter, state_manager)
        
        # Define event handler
        async def handle_event(event_type: str, content: str, agent_id: str = None, role: str = None):
            # Format message based on event type using templates
            if event_type == "conversation_started":
                message = MessageTemplates.conversation_started_message()
            elif event_type == "agent_message":
                message = MessageTemplates.agent_message(role, content, agent_id)
            elif event_type == "user_message":
                message = MessageTemplates.agent_message("user", content, agent_id)
            elif event_type == "user_turn":
                message = MessageTemplates.user_turn_message()
                # Update user state to waiting for input
                state_manager.set_user_state(user_id, ConversationState.WAITING_FOR_USER_INPUT)
            elif event_type == "conversation_completed":
                message = MessageTemplates.conversation_completed_message()
                # Update user state
                state_manager.set_user_state(user_id, ConversationState.CONVERSATION_ENDED)
            elif event_type == "error":
                if content and "401" in content:
                    message = (
                        "❌ **OpenAI authentication failed.** Please double-check the `OPENAI_API_KEY` in your"
                        " server `.env` and redeploy with a valid key."
                    )
                else:
                    message = f"❌ **Error:** {content}"
                state_manager.set_user_state(user_id, ConversationState.ERROR)
            else:
                # Unknown event type, just show content when available
                message = f"📢 {content}" if content else ""
            
            # Send message to user
            if not message:
                return

            try:
                await update.message.reply_text(message, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error sending event message: {e}")
                # Try sending without markdown
                try:
                    await update.message.reply_text(message)
                except Exception as e2:
                    logger.error(f"Error sending plain text message: {e2}")
        
        # Start conversation streaming using service
        await conversation_service.start_conversation_streaming(user_id, handle_event)
        
    except Exception as e:
        logger.error(f"Error streaming conversation events: {e}")
        state_manager.set_user_state(user_id, ConversationState.ERROR)
        
        try:
            await update.message.reply_text(
                MessageTemplates.connection_error_message(),
                parse_mode='Markdown'
            )
        except Exception as e2:
            logger.error(f"Error sending error message: {e2}")


@handle_errors("Error pausing conversation. Please try again.")
async def pause_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Pause an active conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = get_user_id(update)
    state_manager = get_state_manager(context)

    # Check if user is in conversation
    user_state = state_manager.get_user_state(user_id)
    if not user_state.is_in_conversation():
        await update.message.reply_text(Messages.NO_CONVERSATION_TO_PAUSE)
        return
    if not user_state.conversation_id:
        await update.message.reply_text(Messages.NO_CONVERSATION_TO_PAUSE)
        return
    
    # Get adapter and create conversation service
    from ..utils.context_helpers import require_adapter
    adapter = await require_adapter(update, context)
    conversation_service = ConversationService(adapter, state_manager)
    
    # Pause conversation using service
    await conversation_service.pause_conversation(user_id)
    
    # Show confirmation using template
    await update.message.reply_text(
        MessageTemplates.conversation_paused_message(),
        parse_mode='Markdown'
    )


@handle_errors("Error resuming conversation. Please try again.")
async def resume_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Resume a paused conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = get_user_id(update)
    state_manager = get_state_manager(context)

    # Check if user has a paused conversation
    user_state = state_manager.get_user_state(user_id)
    if user_state.state != ConversationState.CONVERSATION_PAUSED:
        await update.message.reply_text(Messages.NO_PAUSED_CONVERSATION)
        return
    if not user_state.conversation_id:
        await update.message.reply_text(Messages.NO_PAUSED_CONVERSATION)
        return
    
    # Get adapter and create conversation service
    from ..utils.context_helpers import require_adapter
    adapter = await require_adapter(update, context)
    conversation_service = ConversationService(adapter, state_manager)
    
    # Resume conversation using service
    await conversation_service.resume_conversation(user_id)
    
    # Show confirmation using template
    await update.message.reply_text(
        MessageTemplates.conversation_resumed_message(),
        parse_mode='Markdown'
    )


@handle_errors("Error stopping conversation. Please try again.")
async def stop_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Stop an active conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = get_user_id(update)
    state_manager = get_state_manager(context)

    # Check if user is in conversation
    user_state = state_manager.get_user_state(user_id)
    if not user_state.is_in_conversation():
        await update.message.reply_text(Messages.NO_CONVERSATION_TO_STOP)
        return
    if not user_state.conversation_id:
        await update.message.reply_text(Messages.NO_CONVERSATION_TO_STOP)
        return
    
    # Get adapter and create conversation service
    from ..utils.context_helpers import require_adapter
    adapter = await require_adapter(update, context)
    conversation_service = ConversationService(adapter, state_manager)
    
    # Stop conversation using service
    await conversation_service.stop_conversation(user_id)
    
    # Show confirmation using template
    await update.message.reply_text(
        MessageTemplates.conversation_stopped_message(),
        parse_mode='Markdown'
    )
