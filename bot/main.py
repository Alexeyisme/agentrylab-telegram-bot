"""Backward compatible entry point exposing key handler modules."""

from .app import main  # noqa: F401
from .handlers import commands, callbacks, messages, presets, conversation  # noqa: F401

# Placeholder adapter reference used by tests that patch bot.main.adapter
adapter = None

__all__ = [
    "main",
    "commands",
    "callbacks",
    "messages",
    "presets",
    "conversation",
    "adapter",
]

if __name__ == "__main__":
    main()
