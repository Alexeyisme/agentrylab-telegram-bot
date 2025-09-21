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

# Import AgentryLab components
try:
    from agentrylab.telegram import TelegramAdapter
except ImportError:
    # Fallback: Create a mock adapter if telegram module doesn't exist
    class TelegramAdapter:
        def __init__(self):
            self.presets = {}
        
        async def get_available_presets(self):
            return [
                {'id': 'debates', 'display_name': 'Debates', 'description': 'AI debate conversations', 'emoji': '🗣️', 'category': 'AI'},
                {'id': 'therapy', 'display_name': 'Therapy', 'description': 'Therapeutic conversations', 'emoji': '🛋️', 'category': 'AI'},
                {'id': 'brainstorm', 'display_name': 'Brainstorming', 'description': 'Creative brainstorming sessions', 'emoji': '💡', 'category': 'AI'}
            ]
        
        async def get_preset_info(self, preset_id):
            return {
                'id': preset_id,
                'display_name': preset_id.title(),
                'description': f'{preset_id} conversation preset',
                'examples': ['Example topic 1', 'Example topic 2']
            }
        
        async def start_conversation(self, user_id, preset_id, topic):
            return f"conv_{user_id}_{preset_id}_{hash(topic) % 10000}"
        
        async def post_user_message(self, conversation_id, user_id, message):
            return True
        
        async def pause_conversation(self, conversation_id):
            return True
        
        async def resume_conversation(self, conversation_id):
            return True
        
        async def stop_conversation(self, conversation_id):
            return True
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
