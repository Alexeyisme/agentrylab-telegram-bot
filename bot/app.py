"""
Simplified main application entry point.
"""

import asyncio
import logging
import sys
import os

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import BotCommand

# Ensure current and parent directories are in Python path
current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)
sys.path.append(os.path.abspath(os.path.join(current_dir, os.pardir)))
from config import BOT_TOKEN, LOG_LEVEL, LOG_FILE, POLLING, WEBHOOK_URL, WEBHOOK_PORT
from .adapters import AsyncTelegramAdapter
from .registry import services
from .states.conversation import ConversationStateManager
from .handlers import commands, callbacks, messages, presets, conversation
from .handlers import callback_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main application entry point (synchronous)."""
    logger.info("Starting AgentryLab Telegram Bot...")
    
    # Initialize AgentryLab adapter
    try:
        adapter = AsyncTelegramAdapter()
        logger.info("AgentryLab adapter initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AgentryLab adapter: {e}")
        sys.exit(1)
    
    # Initialize services
    state_manager = ConversationStateManager()
    services.initialize(adapter, state_manager)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Share core services with handlers via bot_data
    application.bot_data["adapter"] = adapter
    application.bot_data["state_manager"] = state_manager
    
    # Set up handlers
    setup_handlers(application)
    
    # Set up bot commands menu
    setup_bot_commands(application)
    
    # Start the bot
    if POLLING:
        logger.info("Starting bot in polling mode...")
        application.run_polling()
    else:
        logger.info(f"Starting bot in webhook mode on {WEBHOOK_URL}")
        application.run_webhook(
            listen="0.0.0.0",
            port=WEBHOOK_PORT,
            webhook_url=WEBHOOK_URL
        )


def setup_handlers(application: Application) -> None:
    """Set up bot handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", commands.start_command))
    application.add_handler(CommandHandler("help", commands.help_command))
    application.add_handler(CommandHandler("status", commands.status_command))
    application.add_handler(CommandHandler("presets", commands.presets_command))
    application.add_handler(CommandHandler("pause", commands.pause_command))
    application.add_handler(CommandHandler("resume", commands.resume_command))
    application.add_handler(CommandHandler("stop", commands.stop_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(callback_router.handle_callback_query))
    
    # Error handler
    application.add_error_handler(error_handler)


def setup_bot_commands(application: Application) -> None:
    """Set up bot commands menu that appears when users type '/'."""
    bot_commands = [
        BotCommand("start", "🚀 Start a new conversation"),
        BotCommand("help", "❓ Show help and available commands"),
        BotCommand("presets", "🎭 List available conversation types"),
        BotCommand("status", "📊 Check your current status"),
        BotCommand("pause", "⏸️ Pause an active conversation"),
        BotCommand("resume", "▶️ Resume a paused conversation"),
        BotCommand("stop", "⏹️ Stop the current conversation"),
    ]
    
    # Set commands when the application starts
    async def post_init(application):
        await application.bot.set_my_commands(bot_commands)
        logger.info("Bot commands menu set successfully")
    
    # Register the post_init callback
    application.post_init = post_init


async def error_handler(update, context) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again later.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
