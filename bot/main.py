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

async def start_command(update: Update, context) -> None:
    """Handle the /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
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

Use /help for more commands.
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context) -> None:
    """Handle the /help command."""
    help_message = """
📚 **Available Commands:**

/start - Start the bot and see welcome message
/help - Show this help message
/presets - List available conversation types
/status - Show your current conversations
/history - View conversation history

**Conversation Controls:**
• Use inline buttons to control conversations
• Type messages when it's your turn
• Use /stop to end conversations

**Need help?** Contact @your_support_username
    """
    
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def presets_command(update: Update, context) -> None:
    """Handle the /presets command."""
    try:
        # Get available presets from AgentryLab
        presets = adapter.get_available_presets()
        
        if not presets:
            await update.message.reply_text("❌ No presets available. Please check your AgentryLab configuration.")
            return
        
        message = "🎭 **Available Conversation Types:**\n\n"
        for preset_id in presets:
            preset_info = adapter.get_preset_info(preset_id)
            description = preset_info.get('description', 'No description available')
            message += f"• **{preset_id}**: {description}\n"
        
        message += "\nTo start a conversation, just type the preset name or use /start"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting presets: {e}")
        await update.message.reply_text("❌ Error retrieving presets. Please try again later.")

async def status_command(update: Update, context) -> None:
    """Handle the /status command."""
    user_id = str(update.effective_user.id)
    
    try:
        # Get user's active conversations
        active_conversations = []
        for conv_id, state in adapter._conversations.items():
            if state.user_id == user_id and state.status.value == "active":
                active_conversations.append((conv_id, state))
        
        if not active_conversations:
            await update.message.reply_text("📭 You have no active conversations. Use /start to begin!")
            return
        
        message = "📊 **Your Active Conversations:**\n\n"
        for conv_id, state in active_conversations:
            message += f"• **{state.preset_id}** - {state.topic}\n"
            message += f"  Status: {state.status.value}\n"
            message += f"  Iteration: {state.current_iteration}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        await update.message.reply_text("❌ Error retrieving status. Please try again later.")

async def handle_message(update: Update, context) -> None:
    """Handle regular text messages."""
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"User {user.id} sent message: {message_text[:50]}...")
    
    # For now, just echo the message
    # TODO: Implement conversation logic
    await update.message.reply_text(f"Echo: {message_text}")

async def handle_callback_query(update: Update, context) -> None:
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()
    
    # TODO: Implement callback handling
    await query.edit_message_text(f"Button clicked: {query.data}")

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
    except Exception as e:
        logger.error(f"Failed to initialize AgentryLab adapter: {e}")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
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
