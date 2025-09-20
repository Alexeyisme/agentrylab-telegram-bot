"""
Main entry point for the AgentryLab Telegram Bot.

This module initializes the bot, sets up handlers, and starts the polling/webhook.
"""

import asyncio
import logging
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Add the parent directory to the path to import AgentryLab
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentrylab"))

from agentrylab.telegram import TelegramAdapter
from config import (
    BOT_TOKEN, BOT_USERNAME, AGENTRYLAB_PATH, 
    LOG_LEVEL, LOG_FILE, POLLING, WEBHOOK_URL, WEBHOOK_PORT
)

# Import handlers
from .handlers import presets, conversation
from .states.conversation import ConversationStateManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global adapter instance
adapter = None

# Global state manager
state_manager = ConversationStateManager()

async def start_command(update: Update, context) -> None:
    """Handle the /start command."""
    user = update.effective_user
    user_id = str(user.id)
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    # Reset user state
    state_manager.reset_user_state(user_id)
    
    welcome_message = f"""
🤖 **Welcome to AgentryLab!**

Hi {user.first_name}! I'm your gateway to multi-agent conversations.

**What can I do?**
• Start debates between AI agents
• Run stand-up comedy sessions
• Conduct therapy sessions
• Facilitate brainstorming sessions
• And much more!

**How to get started:**
1. Choose a conversation type
2. Enter your topic
3. Watch AI agents interact in real-time
4. Join in when it's your turn!

Click the button below to see available conversation types!
    """
    
    # Create inline keyboard for preset selection
    from .keyboards.presets import create_preset_selection_keyboard
    
    # Get available presets
    try:
        presets_list = adapter.get_available_presets() if adapter else []
        preset_info = {}
        
        for preset_id in presets_list:
            try:
                info = adapter.get_preset_info(preset_id)
                preset_info[preset_id] = {
                    'display_name': info.get('display_name', preset_id.replace('_', ' ').title()),
                    'description': info.get('description', 'Multi-agent conversation'),
                    'emoji': info.get('emoji', '🤖'),
                    'category': info.get('category', 'Other')
                }
            except:
                preset_info[preset_id] = {
                    'display_name': preset_id.replace('_', ' ').title(),
                    'description': 'Multi-agent conversation',
                    'emoji': '🤖',
                    'category': 'Other'
                }
        
        keyboard = create_preset_selection_keyboard(presets_list, preset_info)
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing presets in start command: {e}")
        await update.message.reply_text(
            welcome_message + "\n\nUse /presets to see available conversation types.",
            parse_mode='Markdown'
        )

async def help_command(update: Update, context) -> None:
    """Handle the /help command."""
    help_message = """
📚 **Available Commands:**

**Getting Started:**
/start - Start the bot and see welcome message
/help - Show this help message
/presets - List available conversation types

**Conversation Management:**
/status - Show your current conversation status
/pause - Pause an active conversation
/resume - Resume a paused conversation
/stop - Stop an active conversation

**How to Use:**
1. Use /start to begin
2. Choose a conversation type from the buttons
3. Enter your topic when prompted
4. Watch AI agents interact in real-time
5. Join in when it's your turn!

**Conversation Controls:**
• Use inline buttons to control conversations
• Type messages when it's your turn
• Use commands to pause/resume/stop conversations

**Need help?** Contact @your_support_username
    """
    
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def presets_command(update: Update, context) -> None:
    """Handle the /presets command."""
    await presets.show_presets(update, context)

async def status_command(update: Update, context) -> None:
    """Handle the /status command."""
    user_id = str(update.effective_user.id)
    
    try:
        # Get user state
        user_state = state_manager.get_user_state(user_id)
        
        if not user_state.is_active():
            await update.message.reply_text("📭 You have no active conversations. Use /start to begin!")
            return
        
        message = "📊 **Your Conversation Status:**\n\n"
        message += f"**State:** {user_state.get_state_description()}\n"
        
        if user_state.selected_preset:
            message += f"**Preset:** {user_state.selected_preset}\n"
        
        if user_state.selected_topic:
            message += f"**Topic:** {user_state.selected_topic}\n"
        
        if user_state.conversation_id:
            message += f"**Conversation ID:** {user_state.conversation_id[:8]}...\n"
        
        message += f"**Last Activity:** {user_state.last_activity.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        await update.message.reply_text("❌ Error retrieving status. Please try again later.")


async def pause_command(update: Update, context) -> None:
    """Handle the /pause command."""
    await conversation.pause_conversation(update, context)


async def resume_command(update: Update, context) -> None:
    """Handle the /resume command."""
    await conversation.resume_conversation(update, context)


async def stop_command(update: Update, context) -> None:
    """Handle the /stop command."""
    await conversation.stop_conversation(update, context)

async def handle_message(update: Update, context) -> None:
    """Handle regular text messages."""
    await conversation.handle_topic_input(update, context)

async def handle_callback_query(update: Update, context) -> None:
    """Handle inline keyboard callbacks."""
    await presets.handle_preset_callback(update, context)

async def error_handler(update: Update, context) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again later."
        )

def setup_handlers(application: Application) -> None:
    """Set up all bot handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("presets", presets_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("pause", pause_command))
    application.add_handler(CommandHandler("resume", resume_command))
    application.add_handler(CommandHandler("stop", stop_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Error handler
    application.add_error_handler(error_handler)

async def main() -> None:
    """Main function to start the bot."""
    global adapter
    
    logger.info("Starting AgentryLab Telegram Bot...")
    
    # Initialize AgentryLab adapter
    try:
        adapter = TelegramAdapter()
        logger.info("AgentryLab adapter initialized successfully")
        
        # Store adapter in bot data for handlers to access
        context.bot_data['adapter'] = adapter
        context.bot_data['state_manager'] = state_manager
        
    except Exception as e:
        logger.error(f"Failed to initialize AgentryLab adapter: {e}")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Store adapter and state manager in application
    application.bot_data['adapter'] = adapter
    application.bot_data['state_manager'] = state_manager
    
    # Set up handlers
    setup_handlers(application)
    
    # Start the bot
    if POLLING:
        logger.info("Starting bot in polling mode...")
        await application.run_polling()
    else:
        logger.info(f"Starting bot in webhook mode on {WEBHOOK_URL}")
        await application.run_webhook(
            listen="0.0.0.0",
            port=WEBHOOK_PORT,
            webhook_url=WEBHOOK_URL
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
