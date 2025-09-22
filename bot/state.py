"""
Simplified state management for the bot.
"""

import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone

from .config import (
    STATE_IDLE,
    STATE_WAITING_TOPIC,
    STATE_ACTIVE,
    STATE_PAUSED,
    STATE_ENDED,
)

logger = logging.getLogger(__name__)


@dataclass
class UserState:
    """User conversation state."""

    user_id: str
    state: str = STATE_IDLE
    conversation_id: Optional[str] = None
    preset_id: Optional[str] = None
    topic: Optional[str] = None
    last_activity: Optional[datetime] = None

    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now(timezone.utc)


class BotState:
    """Centralized bot state management."""

    def __init__(self):
        self.users: Dict[str, UserState] = {}
        self.conversations: Dict[str, Dict[str, Any]] = {}

    def get_user_state(self, user_id: str) -> UserState:
        """Get user state, creating if not exists."""
        if user_id not in self.users:
            self.users[user_id] = UserState(user_id=user_id)
        return self.users[user_id]

    def set_user_state(self, user_id: str, state: str, **kwargs) -> None:
        """Set user state with optional additional data."""
        user_state = self.get_user_state(user_id)
        user_state.state = state
        user_state.last_activity = datetime.now(timezone.utc)

        for key, value in kwargs.items():
            if hasattr(user_state, key):
                setattr(user_state, key, value)

    def clear_user_state(self, user_id: str) -> None:
        """Clear user state."""
        if user_id in self.users:
            del self.users[user_id]

    def is_user_in_conversation(self, user_id: str) -> bool:
        """Check if user is in an active conversation."""
        user_state = self.get_user_state(user_id)
        return user_state.state in [STATE_ACTIVE, STATE_PAUSED]

    def get_conversation_users(self, conversation_id: str) -> list:
        """Get all users in a conversation."""
        return [
            user_id
            for user_id, state in self.users.items()
            if state.conversation_id == conversation_id
        ]


# Global state manager
state = BotState()
