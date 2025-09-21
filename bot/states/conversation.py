"""
Conversation state management for the Telegram bot.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum


class ConversationState(Enum):
    """Represents the state of a user's conversation flow."""
    IDLE = "idle"
    SELECTING_PRESET = "selecting_preset"
    ENTERING_TOPIC = "entering_topic"
    CONFIRMING_TOPIC = "confirming_topic"
    STARTING_CONVERSATION = "starting_conversation"
    IN_CONVERSATION = "in_conversation"
    WAITING_FOR_USER_INPUT = "waiting_for_user_input"
    CONVERSATION_PAUSED = "conversation_paused"
    CONVERSATION_ENDED = "conversation_ended"
    ERROR = "error"


@dataclass
class UserConversationState:
    """Represents the state of a user's conversation."""
    user_id: str
    state: ConversationState = ConversationState.IDLE
    selected_preset: Optional[str] = None
    selected_topic: Optional[str] = None
    conversation_id: Optional[str] = None
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Update last activity on initialization."""
        self.last_activity = datetime.now(timezone.utc)
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
    
    def set_state(self, new_state: ConversationState):
        """Set the conversation state and update activity."""
        self.state = new_state
        self.update_activity()
    
    def set_preset(self, preset_id: str):
        """Set the selected preset and update activity."""
        self.selected_preset = preset_id
        self.update_activity()
    
    def set_topic(self, topic: str):
        """Set the selected topic and update activity."""
        self.selected_topic = topic
        self.update_activity()
    
    def set_conversation_id(self, conversation_id: str):
        """Set the conversation ID and update activity."""
        self.conversation_id = conversation_id
        self.update_activity()
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata and update activity."""
        self.metadata[key] = value
        self.update_activity()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def clear_metadata(self):
        """Clear all metadata."""
        self.metadata.clear()
        self.update_activity()
    
    def reset(self):
        """Reset the conversation state to idle."""
        self.state = ConversationState.IDLE
        self.selected_preset = None
        self.selected_topic = None
        self.conversation_id = None
        self.clear_metadata()
        self.update_activity()
    
    def is_active(self) -> bool:
        """Check if the conversation is in an active state."""
        active_states = {
            ConversationState.SELECTING_PRESET,
            ConversationState.ENTERING_TOPIC,
            ConversationState.CONFIRMING_TOPIC,
            ConversationState.STARTING_CONVERSATION,
            ConversationState.IN_CONVERSATION,
            ConversationState.WAITING_FOR_USER_INPUT,
            ConversationState.CONVERSATION_PAUSED
        }
        return self.state in active_states
    
    def is_in_conversation(self) -> bool:
        """Check if the user is currently in a conversation."""
        conversation_states = {
            ConversationState.IN_CONVERSATION,
            ConversationState.WAITING_FOR_USER_INPUT,
            ConversationState.CONVERSATION_PAUSED
        }
        return self.state in conversation_states
    
    def can_start_new_conversation(self) -> bool:
        """Check if the user can start a new conversation."""
        return self.state in {
            ConversationState.IDLE,
            ConversationState.ENTERING_TOPIC,
            ConversationState.CONVERSATION_ENDED,
            ConversationState.ERROR
        }
    
    def get_state_description(self) -> str:
        """Get a human-readable description of the current state."""
        descriptions = {
            ConversationState.IDLE: "Ready to start a new conversation",
            ConversationState.SELECTING_PRESET: "Choosing a conversation type",
            ConversationState.ENTERING_TOPIC: "Entering a topic for the conversation",
            ConversationState.CONFIRMING_TOPIC: "Confirming the topic and starting conversation",
            ConversationState.STARTING_CONVERSATION: "Starting the conversation with AI agents",
            ConversationState.IN_CONVERSATION: "In an active conversation",
            ConversationState.WAITING_FOR_USER_INPUT: "Waiting for your input",
            ConversationState.CONVERSATION_PAUSED: "Conversation is paused",
            ConversationState.CONVERSATION_ENDED: "Conversation has ended",
            ConversationState.ERROR: "An error occurred"
        }
        return descriptions.get(self.state, "Unknown state")


class ConversationStateManager:
    """Manages conversation states for multiple users."""
    
    def __init__(self):
        """Initialize the state manager."""
        self._user_states: Dict[str, UserConversationState] = {}
    
    def get_user_state(self, user_id: str) -> UserConversationState:
        """
        Get the conversation state for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            UserConversationState object
        """
        if user_id not in self._user_states:
            self._user_states[user_id] = UserConversationState(user_id=user_id)
        return self._user_states[user_id]
    
    def set_user_state(self, user_id: str, state: ConversationState):
        """
        Set the conversation state for a user.
        
        Args:
            user_id: The user ID
            state: The new conversation state
        """
        user_state = self.get_user_state(user_id)
        user_state.set_state(state)
    
    def set_user_preset(self, user_id: str, preset_id: str):
        """
        Set the selected preset for a user.
        
        Args:
            user_id: The user ID
            preset_id: The preset ID
        """
        user_state = self.get_user_state(user_id)
        user_state.set_preset(preset_id)
    
    def set_user_topic(self, user_id: str, topic: str):
        """
        Set the selected topic for a user.
        
        Args:
            user_id: The user ID
            topic: The topic text
        """
        user_state = self.get_user_state(user_id)
        user_state.set_topic(topic)
    
    def set_user_conversation_id(self, user_id: str, conversation_id: str):
        """
        Set the conversation ID for a user.
        
        Args:
            user_id: The user ID
            conversation_id: The conversation ID
        """
        user_state = self.get_user_state(user_id)
        user_state.set_conversation_id(conversation_id)
    
    def add_user_metadata(self, user_id: str, key: str, value: Any):
        """
        Add metadata for a user.
        
        Args:
            user_id: The user ID
            key: The metadata key
            value: The metadata value
        """
        user_state = self.get_user_state(user_id)
        user_state.add_metadata(key, value)
    
    def get_user_metadata(self, user_id: str, key: str, default: Any = None) -> Any:
        """
        Get metadata for a user.
        
        Args:
            user_id: The user ID
            key: The metadata key
            default: Default value if key not found
            
        Returns:
            The metadata value
        """
        user_state = self.get_user_state(user_id)
        return user_state.get_metadata(key, default)
    
    def reset_user_state(self, user_id: str):
        """
        Reset the conversation state for a user.
        
        Args:
            user_id: The user ID
        """
        user_state = self.get_user_state(user_id)
        user_state.reset()
    
    def is_user_active(self, user_id: str) -> bool:
        """
        Check if a user has an active conversation.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if user has active conversation
        """
        user_state = self.get_user_state(user_id)
        return user_state.is_active()
    
    def is_user_in_conversation(self, user_id: str) -> bool:
        """
        Check if a user is currently in a conversation.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if user is in conversation
        """
        user_state = self.get_user_state(user_id)
        return user_state.is_in_conversation()
    
    def can_user_start_conversation(self, user_id: str) -> bool:
        """
        Check if a user can start a new conversation.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if user can start conversation
        """
        user_state = self.get_user_state(user_id)
        return user_state.can_start_new_conversation()
    
    def get_user_state_description(self, user_id: str) -> str:
        """
        Get a human-readable description of the user's state.
        
        Args:
            user_id: The user ID
            
        Returns:
            State description
        """
        user_state = self.get_user_state(user_id)
        return user_state.get_state_description()
    
    def get_all_user_states(self) -> Dict[str, UserConversationState]:
        """
        Get all user states.
        
        Returns:
            Dictionary of user states
        """
        return self._user_states.copy()
    
    def get_active_users(self) -> List[str]:
        """
        Get list of users with active conversations.
        
        Returns:
            List of user IDs with active conversations
        """
        return [
            user_id for user_id, state in self._user_states.items()
            if state.is_active()
        ]
    
    def get_users_in_conversation(self) -> List[str]:
        """
        Get list of users currently in conversations.
        
        Returns:
            List of user IDs in conversations
        """
        return [
            user_id for user_id, state in self._user_states.items()
            if state.is_in_conversation()
        ]
    
    def cleanup_inactive_users(self, max_age_hours: int = 24):
        """
        Clean up inactive user states.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        inactive_users = [
            user_id for user_id, state in self._user_states.items()
            if state.last_activity < cutoff_time and not state.is_active()
        ]
        
        for user_id in inactive_users:
            del self._user_states[user_id]
        
        return len(inactive_users)
