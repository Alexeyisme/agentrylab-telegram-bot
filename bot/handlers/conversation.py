"""
Conversation management handlers for the Telegram bot.
"""

import logging
import asyncio
from typing import Optional

from telegram import Update, Message
from telegram.ext import ContextTypes

from ..states.conversation import ConversationState, ConversationStateManager
from ..utils.validation import validate_topic_input

logger = logging.getLogger(__name__)

# Global state manager
state_manager = ConversationStateManager()


async def handle_topic_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle topic input from users.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    message_text = update.message.text.strip()
    
    try:
        # Check if user is waiting for topic input
        if not context.user_data.get('waiting_for_topic', False):
            # User is not in topic input mode, handle as regular message
            await handle_regular_message(update, context)
            return
        
        # Validate topic input
        validation_result = validate_topic_input(message_text)
        if not validation_result['valid']:
            await update.message.reply_text(
                f"❌ {validation_result['error']}\n\n"
                "Please enter a valid topic. For example:\n"
                "• Should remote work become the standard?\n"
                "• How to improve team productivity?\n"
                "• The future of artificial intelligence"
            )
            return
        
        # Get selected preset
        preset_id = context.user_data.get('selected_preset')
        if not preset_id:
            await update.message.reply_text(
                "❌ No preset selected. Please start over with /start"
            )
            return
        
        # Store topic and show confirmation
        context.user_data['selected_topic'] = message_text
        
        # Create confirmation message
        from ..keyboards.presets import (
            create_topic_confirmation_keyboard,
            get_preset_display_name,
            get_preset_emoji
        )
        
        display_name = get_preset_display_name(preset_id)
        emoji = get_preset_emoji(preset_id)
        
        message = f"{emoji} **{display_name}**\n\n"
        message += f"**Topic:** {message_text}\n\n"
        message += "Ready to start the conversation? Click below to begin!"
        
        keyboard = create_topic_confirmation_keyboard(preset_id, message_text)
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
        # Clear waiting state
        context.user_data.pop('waiting_for_topic', None)
        
        # Update user state
        state_manager.set_user_state(user_id, ConversationState.CONFIRMING_TOPIC)
        state_manager.set_user_preset(user_id, preset_id)
        state_manager.set_user_topic(user_id, message_text)
        
    except Exception as e:
        logger.error(f"Error handling topic input: {e}")
        await update.message.reply_text(
            "❌ Error processing your topic. Please try again."
        )


async def handle_regular_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle regular messages from users.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    message_text = update.message.text.strip()
    
    try:
        # Check if user is in a conversation
        if state_manager.is_user_in_conversation(user_id):
            # User is in conversation, handle as conversation input
            await handle_conversation_input(update, context)
            return
        
        # User is not in conversation, provide help
        await update.message.reply_text(
            "🤖 **Hello!** I'm your AgentryLab assistant.\n\n"
            "To get started, use one of these commands:\n"
            "• /start - Start a new conversation\n"
            "• /presets - See available conversation types\n"
            "• /help - Get help and see all commands\n\n"
            "Or just type /start to begin!"
        )
        
    except Exception as e:
        logger.error(f"Error handling regular message: {e}")
        await update.message.reply_text(
            "❌ Error processing your message. Please try again."
        )


async def handle_conversation_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle user input during an active conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    message_text = update.message.text.strip()
    
    try:
        # Get user state
        user_state = state_manager.get_user_state(user_id)
        
        # Check if user is waiting for input
        if user_state.state != ConversationState.WAITING_FOR_USER_INPUT:
            await update.message.reply_text(
                "⏳ Please wait for your turn to speak in the conversation.\n\n"
                "The AI agents are currently discussing. You'll be prompted when it's your turn!"
            )
            return
        
        # Get conversation ID
        conversation_id = user_state.conversation_id
        if not conversation_id:
            await update.message.reply_text(
                "❌ No active conversation found. Please start a new conversation."
            )
            return
        
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            await update.message.reply_text(
                "❌ Bot not properly initialized. Please try again later."
            )
            return
        
        # Post user message to conversation
        try:
            adapter.post_user_message(conversation_id, message_text, user_id=user_id)
            
            # Update user state
            state_manager.set_user_state(user_id, ConversationState.IN_CONVERSATION)
            
            # Show confirmation
            await update.message.reply_text(
                "✅ **Message sent!**\n\n"
                "Your input has been added to the conversation. "
                "The AI agents will continue the discussion."
            )
            
        except Exception as e:
            logger.error(f"Error posting user message: {e}")
            await update.message.reply_text(
                "❌ Error sending your message. Please try again."
            )
        
    except Exception as e:
        logger.error(f"Error handling conversation input: {e}")
        await update.message.reply_text(
            "❌ Error processing your input. Please try again."
        )


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
    user_id = str(update.effective_user.id)
    
    try:
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            await update.message.reply_text(
                "❌ Bot not properly initialized. Please try again later."
            )
            return None
        
        # Update user state
        state_manager.set_user_state(user_id, ConversationState.STARTING_CONVERSATION)
        
        # Start conversation with AgentryLab
        conversation_id = adapter.start_conversation(
            preset_id=preset_id,
            topic=topic,
            user_id=user_id
        )
        
        # Update user state with conversation ID
        state_manager.set_user_conversation_id(user_id, conversation_id)
        state_manager.set_user_state(user_id, ConversationState.IN_CONVERSATION)
        
        # Start conversation streaming task
        asyncio.create_task(stream_conversation_events(update, context, conversation_id))
        
        return conversation_id
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        state_manager.set_user_state(user_id, ConversationState.ERROR)
        await update.message.reply_text(
            "❌ Error starting conversation. Please try again."
        )
        return None


async def stream_conversation_events(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   conversation_id: str) -> None:
    """
    Stream conversation events from AgentryLab.
    
    Args:
        update: Telegram update object
        context: Bot context
        conversation_id: The conversation ID
    """
    user_id = str(update.effective_user.id)
    
    try:
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            return
        
        # Get conversation state
        user_state = state_manager.get_user_state(user_id)
        
        # Stream events
        async for event in adapter.stream_events(conversation_id):
            # Check if conversation is still active
            if not state_manager.is_user_in_conversation(user_id):
                break
            
            # Handle different event types
            event_type = event.event_type
            content = event.content
            agent_id = event.agent_id
            role = event.role
            
            # Format message based on event type
            if event_type == "conversation_started":
                message = "🚀 **Conversation Started!**\n\n"
                message += "The AI agents are now discussing your topic. "
                message += "You'll see their messages in real-time below.\n\n"
                message += "---"
                
            elif event_type == "agent_message":
                # Format agent message
                if role == "user":
                    # This is actually a user message
                    message = f"👤 **You:** {content}"
                elif role == "moderator":
                    message = f"👨‍⚖️ **Moderator:** {content}"
                elif role == "summarizer":
                    message = f"📝 **Summarizer:** {content}"
                else:
                    # Regular agent message
                    agent_name = agent_id or "Agent"
                    message = f"🤖 **{agent_name}:** {content}"
                
            elif event_type == "user_message":
                message = f"👤 **You:** {content}"
                
            elif event_type == "user_turn":
                message = "👤 **It's your turn!** What would you like to say?\n\n"
                message += "Type your message below:"
                
                # Update user state to waiting for input
                state_manager.set_user_state(user_id, ConversationState.WAITING_FOR_USER_INPUT)
                
            elif event_type == "conversation_completed":
                message = "✅ **Conversation Completed!**\n\n"
                message += "The discussion has ended. Thank you for participating!\n\n"
                message += "Use /start to begin a new conversation."
                
                # Update user state
                state_manager.set_user_state(user_id, ConversationState.CONVERSATION_ENDED)
                
            elif event_type == "error":
                message = f"❌ **Error:** {content}"
                state_manager.set_user_state(user_id, ConversationState.ERROR)
                
            else:
                # Unknown event type, just show content
                message = f"📢 {content}"
            
            # Send message to user
            try:
                await update.message.reply_text(message, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error sending event message: {e}")
                # Try sending without markdown
                try:
                    await update.message.reply_text(message)
                except Exception as e2:
                    logger.error(f"Error sending plain text message: {e2}")
        
    except Exception as e:
        logger.error(f"Error streaming conversation events: {e}")
        state_manager.set_user_state(user_id, ConversationState.ERROR)
        
        try:
            await update.message.reply_text(
                "❌ **Connection Error**\n\n"
                "The conversation connection was lost. "
                "Please start a new conversation with /start."
            )
        except Exception as e2:
            logger.error(f"Error sending error message: {e2}")


async def pause_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Pause an active conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    try:
        # Check if user is in conversation
        if not state_manager.is_user_in_conversation(user_id):
            await update.message.reply_text(
                "❌ You don't have an active conversation to pause."
            )
            return
        
        # Get conversation ID
        user_state = state_manager.get_user_state(user_id)
        conversation_id = user_state.conversation_id
        
        if not conversation_id:
            await update.message.reply_text(
                "❌ No active conversation found."
            )
            return
        
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            await update.message.reply_text(
                "❌ Bot not properly initialized. Please try again later."
            )
            return
        
        # Pause conversation
        adapter.pause_conversation(conversation_id)
        
        # Update user state
        state_manager.set_user_state(user_id, ConversationState.CONVERSATION_PAUSED)
        
        await update.message.reply_text(
            "⏸️ **Conversation Paused**\n\n"
            "The conversation has been paused. Use /resume to continue."
        )
        
    except Exception as e:
        logger.error(f"Error pausing conversation: {e}")
        await update.message.reply_text(
            "❌ Error pausing conversation. Please try again."
        )


async def resume_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Resume a paused conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    try:
        # Check if user has a paused conversation
        user_state = state_manager.get_user_state(user_id)
        if user_state.state != ConversationState.CONVERSATION_PAUSED:
            await update.message.reply_text(
                "❌ You don't have a paused conversation to resume."
            )
            return
        
        # Get conversation ID
        conversation_id = user_state.conversation_id
        
        if not conversation_id:
            await update.message.reply_text(
                "❌ No paused conversation found."
            )
            return
        
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            await update.message.reply_text(
                "❌ Bot not properly initialized. Please try again later."
            )
            return
        
        # Resume conversation
        adapter.resume_conversation(conversation_id)
        
        # Update user state
        state_manager.set_user_state(user_id, ConversationState.IN_CONVERSATION)
        
        await update.message.reply_text(
            "▶️ **Conversation Resumed**\n\n"
            "The conversation has been resumed. The AI agents will continue."
        )
        
    except Exception as e:
        logger.error(f"Error resuming conversation: {e}")
        await update.message.reply_text(
            "❌ Error resuming conversation. Please try again."
        )


async def stop_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Stop an active conversation.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    user_id = str(update.effective_user.id)
    
    try:
        # Check if user is in conversation
        if not state_manager.is_user_in_conversation(user_id):
            await update.message.reply_text(
                "❌ You don't have an active conversation to stop."
            )
            return
        
        # Get conversation ID
        user_state = state_manager.get_user_state(user_id)
        conversation_id = user_state.conversation_id
        
        if not conversation_id:
            await update.message.reply_text(
                "❌ No active conversation found."
            )
            return
        
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            await update.message.reply_text(
                "❌ Bot not properly initialized. Please try again later."
            )
            return
        
        # Stop conversation
        adapter.stop_conversation(conversation_id)
        
        # Update user state
        state_manager.set_user_state(user_id, ConversationState.CONVERSATION_ENDED)
        
        await update.message.reply_text(
            "⏹️ **Conversation Stopped**\n\n"
            "The conversation has been ended. Use /start to begin a new one."
        )
        
    except Exception as e:
        logger.error(f"Error stopping conversation: {e}")
        await update.message.reply_text(
            "❌ Error stopping conversation. Please try again."
        )
