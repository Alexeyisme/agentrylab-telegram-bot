"""
Callback router for handling Telegram inline keyboard callbacks.

This module provides a clean routing system for callback queries,
replacing the complex if-elif chains with a more maintainable pattern.
"""

import logging
from typing import Dict, Callable, Any, Optional
from telegram import CallbackQuery
from telegram.ext import ContextTypes

from ..constants import CallbackPrefixes, Messages
from ..utils.error_handling import handle_callback_errors

logger = logging.getLogger(__name__)


class CallbackRouter:
    """
    Router for handling callback queries with prefix-based routing.
    
    This class provides a clean way to handle different types of callback
    queries by registering handlers for specific prefixes.
    """
    
    def __init__(self):
        """Initialize the callback router."""
        self.handlers: Dict[str, Callable] = {}
        self.default_handler: Optional[Callable] = None
    
    def register(self, prefix: str, handler_func: Callable) -> None:
        """
        Register a handler for a callback prefix.
        
        Args:
            prefix: Callback data prefix (e.g., "preset_", "select_")
            handler_func: Function to handle callbacks with this prefix
        """
        self.handlers[prefix] = handler_func
        logger.debug(f"Registered callback handler for prefix: {prefix}")
    
    def register_default(self, handler_func: Callable) -> None:
        """
        Register a default handler for unmatched callbacks.
        
        Args:
            handler_func: Function to handle unmatched callbacks
        """
        self.default_handler = handler_func
        logger.debug("Registered default callback handler")
    
    @handle_callback_errors("An error occurred processing your request.")
    async def handle_callback(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> Any:
        """
        Route callback to appropriate handler based on data prefix.
        
        Args:
            query: Callback query object
            context: Bot context
            
        Returns:
            Result from the appropriate handler
        """
        data = query.data
        if not data:
            return
        
        logger.debug(f"Handling callback with data: {data}")
        
        # Find matching handler
        for prefix, handler in self.handlers.items():
            if data.startswith(prefix):
                callback_data = data.replace(prefix, "", 1)
                logger.debug(f"Routing to handler for prefix '{prefix}' with data: {callback_data}")
                return await handler(query, context, callback_data)
        
        # Handle special cases
        if data == CallbackPrefixes.BACK_TO_PRESETS:
            return await self._handle_back_to_presets(query, context)
        elif data == CallbackPrefixes.PRESET_INFO:
            return await self._handle_preset_info(query, context)
        elif data == CallbackPrefixes.CANCEL:
            return await self._handle_cancel(query, context)
        elif data == CallbackPrefixes.CATEGORY_HEADER:
            return await self._handle_category_header(query, context)
        
        # Use default handler if available
        if self.default_handler:
            logger.debug("Using default handler for unmatched callback")
            return await self.default_handler(query, context, data)
        
        # No handler found
        logger.warning(f"No handler found for callback data: {data}")
        await query.edit_message_text(Messages.UNKNOWN_ACTION)
    
    async def _handle_back_to_presets(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle back to presets callback."""
        from .presets import show_presets_callback
        await show_presets_callback(query, context)
    
    async def _handle_preset_info(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle preset info callback."""
        from .presets import show_general_preset_info
        await show_general_preset_info(query, context)
    
    async def _handle_cancel(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle cancel callback."""
        await query.edit_message_text(Messages.OPERATION_CANCELLED)
    
    async def _handle_category_header(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle category header callback (no action needed)."""
        # Category headers are just visual, no action needed
        pass
    
    def get_registered_prefixes(self) -> list:
        """
        Get list of registered callback prefixes.
        
        Returns:
            List of registered prefixes
        """
        return list(self.handlers.keys())
    
    def is_registered(self, prefix: str) -> bool:
        """
        Check if a prefix is registered.
        
        Args:
            prefix: Prefix to check
            
        Returns:
            True if prefix is registered
        """
        return prefix in self.handlers


class PresetCallbackRouter(CallbackRouter):
    """
    Specialized callback router for preset-related callbacks.
    
    This router handles all preset-related callback queries with
    appropriate error handling and logging.
    """
    
    def __init__(self):
        """Initialize the preset callback router."""
        super().__init__()
        self._register_preset_handlers()
    
    def _register_preset_handlers(self) -> None:
        """Register all preset-related callback handlers."""
        from . import presets
        
        # Register preset handlers
        self.register(CallbackPrefixes.PRESET, presets.show_preset_info)
        self.register(CallbackPrefixes.SELECT, presets.start_custom_topic_input)
        self.register(CallbackPrefixes.EXAMPLES, presets.show_preset_examples)
        self.register(CallbackPrefixes.EXAMPLE, presets.use_example_topic)
        self.register(CallbackPrefixes.CUSTOM, presets.start_custom_topic_input)
        self.register(CallbackPrefixes.START, presets.start_conversation)
        self.register(CallbackPrefixes.EDIT, presets.start_custom_topic_input)
        
        # Set default handler
        self.register_default(self._handle_unknown_preset_callback)
    
    async def _handle_unknown_preset_callback(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle unknown preset callbacks."""
        logger.warning(f"Unknown preset callback: {data}")
        await query.edit_message_text(Messages.UNKNOWN_ACTION)


class ConversationCallbackRouter(CallbackRouter):
    """
    Specialized callback router for conversation-related callbacks.
    
    This router handles conversation control callbacks like pause, resume, stop.
    """
    
    def __init__(self):
        """Initialize the conversation callback router."""
        super().__init__()
        self._register_conversation_handlers()
    
    def _register_conversation_handlers(self) -> None:
        """Register conversation-related callback handlers."""
        # Register conversation handlers
        self.register("pause_", self._handle_pause_conversation)
        self.register("resume_", self._handle_resume_conversation)
        self.register("stop_", self._handle_stop_conversation)
        self.register("restart_", self._handle_restart_conversation)
        
        # Set default handler
        self.register_default(self._handle_unknown_conversation_callback)
    
    async def _handle_pause_conversation(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle pause conversation callback."""
        from .conversation import pause_conversation
        # Convert callback query to update-like object for compatibility
        class MockUpdate:
            def __init__(self, callback_query):
                self.callback_query = callback_query
                self.message = None
                self.effective_user = callback_query.from_user
        
        mock_update = MockUpdate(query)
        await pause_conversation(mock_update, context)
    
    async def _handle_resume_conversation(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle resume conversation callback."""
        from .conversation import resume_conversation
        # Convert callback query to update-like object for compatibility
        class MockUpdate:
            def __init__(self, callback_query):
                self.callback_query = callback_query
                self.message = None
                self.effective_user = callback_query.from_user
        
        mock_update = MockUpdate(query)
        await resume_conversation(mock_update, context)
    
    async def _handle_stop_conversation(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle stop conversation callback."""
        from .conversation import stop_conversation
        # Convert callback query to update-like object for compatibility
        class MockUpdate:
            def __init__(self, callback_query):
                self.callback_query = callback_query
                self.message = None
                self.effective_user = callback_query.from_user
        
        mock_update = MockUpdate(query)
        await stop_conversation(mock_update, context)
    
    async def _handle_restart_conversation(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle restart conversation callback."""
        # TODO: Implement restart conversation functionality
        await query.edit_message_text("🔄 Restart functionality coming soon!")
    
    async def _handle_unknown_conversation_callback(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle unknown conversation callbacks."""
        logger.warning(f"Unknown conversation callback: {data}")
        await query.edit_message_text(Messages.UNKNOWN_ACTION)


# Global router instances
preset_router = PresetCallbackRouter()
conversation_router = ConversationCallbackRouter()


def get_callback_router(callback_type: str = "preset") -> CallbackRouter:
    """
    Get the appropriate callback router for the given type.
    
    Args:
        callback_type: Type of router to get ("preset" or "conversation")
        
    Returns:
        Appropriate callback router instance
    """
    routers = {
        "preset": preset_router,
        "conversation": conversation_router
    }
    
    return routers.get(callback_type, preset_router)


async def handle_callback_query(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Main callback query handler that routes to appropriate router.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    query = update.callback_query
    data = query.data
    
    # Determine router type based on callback data
    if any(data.startswith(prefix) for prefix in [
        CallbackPrefixes.PRESET,
        CallbackPrefixes.SELECT,
        CallbackPrefixes.EXAMPLES,
        CallbackPrefixes.EXAMPLE,
        CallbackPrefixes.CUSTOM,
        CallbackPrefixes.START,
        CallbackPrefixes.EDIT
    ]):
        router = get_callback_router("preset")
    elif any(data.startswith(prefix) for prefix in ["pause_", "resume_", "stop_", "restart_"]):
        router = get_callback_router("conversation")
    else:
        # Default to preset router for unknown callbacks
        router = get_callback_router("preset")
    
    await router.handle_callback(query, context)
