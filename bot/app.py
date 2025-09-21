"""
Simplified main application entry point.
"""

import asyncio
import logging
import sys
from pathlib import Path

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Add AgentryLab to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentrylab"))

from agentrylab.telegram import TelegramAdapter
from .config import BOT_TOKEN, LOG_LEVEL, LOG_FILE, POLLING, WEBHOOK_URL, WEBHOOK_PORT
from .registry import services
from .state import state
from .handlers import commands, callbacks, messages

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


async def main() -> None:
    """Main application entry point."""
    logger.info("Starting AgentryLab Telegram Bot...")
    
    # Initialize AgentryLab adapter
    try:
        adapter = TelegramAdapter()
        logger.info("AgentryLab adapter initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AgentryLab adapter: {e}")
        sys.exit(1)
    
    # Initialize services
    services.initialize(adapter, state)
    
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


def setup_handlers(application: Application) -> None:
    """Set up bot handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", commands.start_command))
    application.add_handler(CommandHandler("help", commands.help_command))
    application.add_handler(CommandHandler("status", commands.status_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(callbacks.handle_callback))
    
    # Error handler
    application.add_error_handler(error_handler)


async def error_handler(update, context) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again later.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
