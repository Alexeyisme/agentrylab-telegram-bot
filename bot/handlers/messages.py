"""
Simplified message handlers.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import MAX_TOPIC_LENGTH
from ..services import services
from ..constants import ConversationStates

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user_id = str(update.effective_user.id)
    message_text = update.message.text.strip()
    user_state = services.state_manager.get_user_state(user_id)
    
    # Handle topic input
    if user_state.state == ConversationStates.ENTERING_TOPIC:
        await handle_topic_input(update, context, message_text)
    # Handle conversation input
    elif user_state.state == ConversationStates.IN_CONVERSATION:
        await handle_conversation_input(update, context, message_text)
    # Handle regular messages
    else:
        await handle_regular_message(update, context, message_text)


async def handle_topic_input(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str) -> None:
    """Handle topic input from user."""
    user_id = str(update.effective_user.id)
    user_state = services.state_manager.get_user_state(user_id)
    
    # Validate topic
    if len(topic) > MAX_TOPIC_LENGTH:
        await update.message.reply_text(
            f"❌ Topic too long. Maximum {MAX_TOPIC_LENGTH} characters."
        )
        return
    
    if not topic.strip():
        await update.message.reply_text("❌ Please enter a valid topic.")
        return
    
    # Store topic and start conversation
    try:
        conversation_service = services.get_conversation_service()
        conversation_id = await conversation_service.start_conversation(
            user_id, user_state.selected_preset, topic
        )
        
        await update.message.reply_text(
            f"🚀 **Conversation Started!**\n\n"
            f"Preset: {user_state.selected_preset}\n"
            f"Topic: {topic}\n\n"
            f"Watch the agents interact in real-time!",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await update.message.reply_text("❌ Error starting conversation. Please try again.")


async def handle_conversation_input(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    """Handle user input during conversation."""
    user_id = str(update.effective_user.id)
    user_state = services.state_manager.get_user_state(user_id)
    
    if not user_state.conversation_id:
        await update.message.reply_text("❌ No active conversation found.")
        return
    
    try:
        conversation_service = services.get_conversation_service()
        success = await conversation_service.handle_user_input(user_id, message)
        
        if success:
            await update.message.reply_text("✅ **Message sent!**", parse_mode='Markdown')
        else:
            await update.message.reply_text("⏳ Please wait for your turn to speak.")
            
    except Exception as e:
        logger.error(f"Error handling user input: {e}")
        await update.message.reply_text("❌ Error sending message. Please try again.")


async def handle_regular_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    """Handle regular messages when not in conversation."""
    await update.message.reply_text(
        "🤖 Use /start to begin a new conversation or /help for more information."
    )
