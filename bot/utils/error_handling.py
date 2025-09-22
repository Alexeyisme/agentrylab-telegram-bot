"""
Error handling utilities for the Telegram bot.

This module provides decorators and utilities for consistent error handling
across all bot handlers, reducing code duplication and improving maintainability.
"""

import logging
from functools import wraps
from typing import Callable, Any, Optional
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class BotError(Exception):
    """Base exception for bot-specific errors."""

    pass


class BotNotInitializedError(BotError):
    """Raised when the bot is not properly initialized."""

    pass


class UserNotActiveError(BotError):
    """Raised when user has no active conversation."""

    pass


class ConversationNotFoundError(BotError):
    """Raised when conversation is not found."""

    pass


def handle_errors(
    error_message: str = "An error occurred. Please try again.",
    log_error: bool = True,
    reraise: bool = False,
) -> Callable:
    """
    Decorator for consistent error handling in bot handlers.

    Args:
        error_message: User-friendly error message to send
        log_error: Whether to log the error
        reraise: Whether to reraise the exception after handling

    Returns:
        Decorated function with error handling
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ) -> Any:
            try:
                return await func(update, context, *args, **kwargs)
            except BotError as e:
                # Handle bot-specific errors
                if log_error:
                    logger.warning(f"Bot error in {func.__name__}: {e}")
                await _send_error_message(update, str(e))
                if reraise:
                    raise
            except Exception as e:
                # Handle unexpected errors
                if log_error:
                    logger.error(
                        f"Unexpected error in {func.__name__}: {e}", exc_info=True
                    )
                await _send_error_message(update, error_message)
                if reraise:
                    raise

        return wrapper

    return decorator


async def _send_error_message(update: Update, message: str) -> None:
    """
    Send error message to user.

    Args:
        update: Telegram update object
        message: Error message to send
    """
    try:
        if update.message:
            await update.message.reply_text(f"❌ {message}")
        elif update.callback_query:
            await update.callback_query.edit_message_text(f"❌ {message}")
    except Exception as e:
        logger.error(f"Failed to send error message: {e}")


def handle_callback_errors(
    error_message: str = "An error occurred. Please try again.", log_error: bool = True
) -> Callable:
    """
    Decorator for error handling in callback query handlers.

    Args:
        error_message: User-friendly error message to send
        log_error: Whether to log the error

    Returns:
        Decorated function with error handling
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            query, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ) -> Any:
            try:
                return await func(query, context, *args, **kwargs)
            except BotError as e:
                if log_error:
                    logger.warning(f"Bot error in {func.__name__}: {e}")
                await query.edit_message_text(f"❌ {e}")
            except Exception as e:
                if log_error:
                    logger.error(
                        f"Unexpected error in {func.__name__}: {e}", exc_info=True
                    )
                await query.edit_message_text(f"❌ {error_message}")

        return wrapper

    return decorator


def safe_async_call(func: Callable, *args, **kwargs) -> Any:
    """
    Safely call an async function with error handling.

    Args:
        func: Async function to call
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result or None if error occurred
    """
    import asyncio

    try:
        if asyncio.iscoroutinefunction(func):
            return asyncio.create_task(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in safe_async_call for {func.__name__}: {e}")
        return None


class ErrorContext:
    """Context manager for error handling with custom messages."""

    def __init__(self, error_message: str, log_error: bool = True):
        self.error_message = error_message
        self.log_error = log_error
        self.error_occurred = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_occurred = True
            if self.log_error:
                logger.error(f"Error in context: {exc_val}", exc_info=exc_tb)
            return True  # Suppress the exception
        return False


def log_function_call(func_name: str, **kwargs) -> None:
    """
    Log function call with parameters.

    Args:
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"Calling {func_name}({params})")


def log_function_result(func_name: str, result: Any = None, **kwargs) -> None:
    """
    Log function result.

    Args:
        func_name: Name of the function
        result: Function result
        **kwargs: Additional context
    """
    context = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"{func_name} completed. Result: {result}. Context: {context}")
