"""
Simplified command handlers.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..config import WELCOME_MSG, HELP_MSG, NO_CONVERSATION_MSG
from ..services import services
from ..constants import ConversationStates

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name or "User"
    
    # Clear any existing state
    services.state_manager.reset_user_state(user_id)
    
    # Send welcome message
    await update.message.reply_text(
        WELCOME_MSG.format(name=user_name),
        parse_mode='Markdown'
    )
    
    # Show presets
    await show_presets(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(HELP_MSG, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command."""
    user_id = str(update.effective_user.id)
    user_state = services.state_manager.get_user_state(user_id)
    
    if not services.state_manager.is_user_in_conversation(user_id):
        await update.message.reply_text(NO_CONVERSATION_MSG)
        return
    
    status_msg = f"📊 **Your Status**\n\n"
    status_msg += f"**State:** {user_state.state.value}\n"
    status_msg += f"**Preset:** {user_state.selected_preset}\n"
    status_msg += f"**Topic:** {user_state.selected_topic}\n"
    
    await update.message.reply_text(status_msg, parse_mode='Markdown')


async def show_presets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available presets."""
    try:
        preset_service = services.get_preset_service()
        presets = await preset_service.get_available_presets()
        
        if not presets:
            await update.message.reply_text("❌ No presets available.")
            return
        
        # Create simple keyboard
        from ..keyboards.presets import create_preset_selection_keyboard
        preset_info = await preset_service.get_preset_info_batch(presets)
        keyboard = create_preset_selection_keyboard(presets, preset_info)
        
        await update.message.reply_text(
            "🎭 **Choose a conversation type:**",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing presets: {e}")
        await update.message.reply_text("❌ Error loading presets. Please try again.")
