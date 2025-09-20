"""
Tests for conversation state management.
"""

import pytest
from datetime import datetime, timezone, timedelta

from bot.states.conversation import (
    ConversationState,
    UserConversationState,
    ConversationStateManager
)


class TestConversationState:
    """Test ConversationState enum."""
    
    def test_conversation_state_values(self):
        """Test that conversation states have correct values."""
        assert ConversationState.IDLE.value == "idle"
        assert ConversationState.SELECTING_PRESET.value == "selecting_preset"
        assert ConversationState.ENTERING_TOPIC.value == "entering_topic"
        assert ConversationState.CONFIRMING_TOPIC.value == "confirming_topic"
        assert ConversationState.STARTING_CONVERSATION.value == "starting_conversation"
        assert ConversationState.IN_CONVERSATION.value == "in_conversation"
        assert ConversationState.WAITING_FOR_USER_INPUT.value == "waiting_for_user_input"
        assert ConversationState.CONVERSATION_PAUSED.value == "conversation_paused"
        assert ConversationState.CONVERSATION_ENDED.value == "conversation_ended"
        assert ConversationState.ERROR.value == "error"


class TestUserConversationState:
    """Test UserConversationState class."""
    
    def test_user_conversation_state_creation(self):
        """Test creating a user conversation state."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        assert state.user_id == user_id
        assert state.state == ConversationState.IDLE
        assert state.selected_preset is None
        assert state.selected_topic is None
        assert state.conversation_id is None
        assert isinstance(state.last_activity, datetime)
        assert isinstance(state.metadata, dict)
        assert len(state.metadata) == 0
    
    def test_update_activity(self):
        """Test updating activity timestamp."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        original_activity = state.last_activity
        state.update_activity()
        
        assert state.last_activity > original_activity
    
    def test_set_state(self):
        """Test setting conversation state."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        state.set_state(ConversationState.SELECTING_PRESET)
        assert state.state == ConversationState.SELECTING_PRESET
    
    def test_set_preset(self):
        """Test setting selected preset."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        state.set_preset("debates")
        assert state.selected_preset == "debates"
    
    def test_set_topic(self):
        """Test setting selected topic."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        state.set_topic("Remote work vs office")
        assert state.selected_topic == "Remote work vs office"
    
    def test_set_conversation_id(self):
        """Test setting conversation ID."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        conversation_id = "12345678-1234-1234-1234-123456789012"
        state.set_conversation_id(conversation_id)
        assert state.conversation_id == conversation_id
    
    def test_add_metadata(self):
        """Test adding metadata."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        state.add_metadata("key1", "value1")
        state.add_metadata("key2", 42)
        
        assert state.metadata["key1"] == "value1"
        assert state.metadata["key2"] == 42
    
    def test_get_metadata(self):
        """Test getting metadata."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        state.add_metadata("key1", "value1")
        
        assert state.get_metadata("key1") == "value1"
        assert state.get_metadata("nonexistent") is None
        assert state.get_metadata("nonexistent", "default") == "default"
    
    def test_clear_metadata(self):
        """Test clearing metadata."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        state.add_metadata("key1", "value1")
        state.add_metadata("key2", "value2")
        
        assert len(state.metadata) == 2
        state.clear_metadata()
        assert len(state.metadata) == 0
    
    def test_reset(self):
        """Test resetting conversation state."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        # Set some values
        state.set_state(ConversationState.IN_CONVERSATION)
        state.set_preset("debates")
        state.set_topic("Test topic")
        state.set_conversation_id("test-id")
        state.add_metadata("key", "value")
        
        # Reset
        state.reset()
        
        assert state.state == ConversationState.IDLE
        assert state.selected_preset is None
        assert state.selected_topic is None
        assert state.conversation_id is None
        assert len(state.metadata) == 0
    
    def test_is_active(self):
        """Test checking if conversation is active."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        # Initially idle
        assert not state.is_active()
        
        # Active states
        state.set_state(ConversationState.SELECTING_PRESET)
        assert state.is_active()
        
        state.set_state(ConversationState.IN_CONVERSATION)
        assert state.is_active()
        
        state.set_state(ConversationState.WAITING_FOR_USER_INPUT)
        assert state.is_active()
        
        # Inactive states
        state.set_state(ConversationState.IDLE)
        assert not state.is_active()
        
        state.set_state(ConversationState.CONVERSATION_ENDED)
        assert not state.is_active()
        
        state.set_state(ConversationState.ERROR)
        assert not state.is_active()
    
    def test_is_in_conversation(self):
        """Test checking if user is in conversation."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        # Initially idle
        assert not state.is_in_conversation()
        
        # In conversation states
        state.set_state(ConversationState.IN_CONVERSATION)
        assert state.is_in_conversation()
        
        state.set_state(ConversationState.WAITING_FOR_USER_INPUT)
        assert state.is_in_conversation()
        
        state.set_state(ConversationState.CONVERSATION_PAUSED)
        assert state.is_in_conversation()
        
        # Not in conversation states
        state.set_state(ConversationState.IDLE)
        assert not state.is_in_conversation()
        
        state.set_state(ConversationState.SELECTING_PRESET)
        assert not state.is_in_conversation()
    
    def test_can_start_new_conversation(self):
        """Test checking if user can start new conversation."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
        # Can start new conversation
        assert state.can_start_new_conversation()
        
        state.set_state(ConversationState.CONVERSATION_ENDED)
        assert state.can_start_new_conversation()
        
        state.set_state(ConversationState.ERROR)
        assert state.can_start_new_conversation()
        
        # Cannot start new conversation
        state.set_state(ConversationState.SELECTING_PRESET)
        assert not state.can_start_new_conversation()
        
        state.set_state(ConversationState.IN_CONVERSATION)
        assert not state.can_start_new_conversation()
    
    def test_get_state_description(self):
        """Test getting state description."""
        user_id = "123456789"
        state = UserConversationState(user_id=user_id)
        
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
        
        for state_enum, expected_description in descriptions.items():
            state.set_state(state_enum)
            assert state.get_state_description() == expected_description


class TestConversationStateManager:
    """Test ConversationStateManager class."""
    
    def test_conversation_state_manager_creation(self):
        """Test creating a conversation state manager."""
        manager = ConversationStateManager()
        
        assert isinstance(manager._user_states, dict)
        assert len(manager._user_states) == 0
    
    def test_get_user_state_new_user(self):
        """Test getting state for new user."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        state = manager.get_user_state(user_id)
        
        assert isinstance(state, UserConversationState)
        assert state.user_id == user_id
        assert state.state == ConversationState.IDLE
    
    def test_get_user_state_existing_user(self):
        """Test getting state for existing user."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        # Get state twice
        state1 = manager.get_user_state(user_id)
        state2 = manager.get_user_state(user_id)
        
        assert state1 is state2  # Same object
    
    def test_set_user_state(self):
        """Test setting user state."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        manager.set_user_state(user_id, ConversationState.SELECTING_PRESET)
        
        state = manager.get_user_state(user_id)
        assert state.state == ConversationState.SELECTING_PRESET
    
    def test_set_user_preset(self):
        """Test setting user preset."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        manager.set_user_preset(user_id, "debates")
        
        state = manager.get_user_state(user_id)
        assert state.selected_preset == "debates"
    
    def test_set_user_topic(self):
        """Test setting user topic."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        manager.set_user_topic(user_id, "Test topic")
        
        state = manager.get_user_state(user_id)
        assert state.selected_topic == "Test topic"
    
    def test_set_user_conversation_id(self):
        """Test setting user conversation ID."""
        manager = ConversationStateManager()
        user_id = "123456789"
        conversation_id = "12345678-1234-1234-1234-123456789012"
        
        manager.set_user_conversation_id(user_id, conversation_id)
        
        state = manager.get_user_state(user_id)
        assert state.conversation_id == conversation_id
    
    def test_add_user_metadata(self):
        """Test adding user metadata."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        manager.add_user_metadata(user_id, "key", "value")
        
        state = manager.get_user_state(user_id)
        assert state.metadata["key"] == "value"
    
    def test_get_user_metadata(self):
        """Test getting user metadata."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        manager.add_user_metadata(user_id, "key", "value")
        
        assert manager.get_user_metadata(user_id, "key") == "value"
        assert manager.get_user_metadata(user_id, "nonexistent") is None
        assert manager.get_user_metadata(user_id, "nonexistent", "default") == "default"
    
    def test_reset_user_state(self):
        """Test resetting user state."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        # Set some values
        manager.set_user_state(user_id, ConversationState.IN_CONVERSATION)
        manager.set_user_preset(user_id, "debates")
        manager.set_user_topic(user_id, "Test topic")
        
        # Reset
        manager.reset_user_state(user_id)
        
        state = manager.get_user_state(user_id)
        assert state.state == ConversationState.IDLE
        assert state.selected_preset is None
        assert state.selected_topic is None
    
    def test_is_user_active(self):
        """Test checking if user is active."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        # Initially not active
        assert not manager.is_user_active(user_id)
        
        # Set active state
        manager.set_user_state(user_id, ConversationState.SELECTING_PRESET)
        assert manager.is_user_active(user_id)
        
        # Set inactive state
        manager.set_user_state(user_id, ConversationState.IDLE)
        assert not manager.is_user_active(user_id)
    
    def test_is_user_in_conversation(self):
        """Test checking if user is in conversation."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        # Initially not in conversation
        assert not manager.is_user_in_conversation(user_id)
        
        # Set in conversation state
        manager.set_user_state(user_id, ConversationState.IN_CONVERSATION)
        assert manager.is_user_in_conversation(user_id)
        
        # Set not in conversation state
        manager.set_user_state(user_id, ConversationState.IDLE)
        assert not manager.is_user_in_conversation(user_id)
    
    def test_can_user_start_conversation(self):
        """Test checking if user can start conversation."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        # Can start conversation
        assert manager.can_user_start_conversation(user_id)
        
        # Cannot start conversation
        manager.set_user_state(user_id, ConversationState.SELECTING_PRESET)
        assert not manager.can_user_start_conversation(user_id)
    
    def test_get_user_state_description(self):
        """Test getting user state description."""
        manager = ConversationStateManager()
        user_id = "123456789"
        
        manager.set_user_state(user_id, ConversationState.SELECTING_PRESET)
        
        description = manager.get_user_state_description(user_id)
        assert description == "Choosing a conversation type"
    
    def test_get_all_user_states(self):
        """Test getting all user states."""
        manager = ConversationStateManager()
        
        # Add some users
        manager.get_user_state("user1")
        manager.get_user_state("user2")
        
        all_states = manager.get_all_user_states()
        
        assert len(all_states) == 2
        assert "user1" in all_states
        assert "user2" in all_states
    
    def test_get_active_users(self):
        """Test getting active users."""
        manager = ConversationStateManager()
        
        # Add users with different states
        manager.set_user_state("user1", ConversationState.IDLE)
        manager.set_user_state("user2", ConversationState.SELECTING_PRESET)
        manager.set_user_state("user3", ConversationState.IN_CONVERSATION)
        
        active_users = manager.get_active_users()
        
        assert len(active_users) == 2
        assert "user2" in active_users
        assert "user3" in active_users
        assert "user1" not in active_users
    
    def test_get_users_in_conversation(self):
        """Test getting users in conversation."""
        manager = ConversationStateManager()
        
        # Add users with different states
        manager.set_user_state("user1", ConversationState.SELECTING_PRESET)
        manager.set_user_state("user2", ConversationState.IN_CONVERSATION)
        manager.set_user_state("user3", ConversationState.WAITING_FOR_USER_INPUT)
        manager.set_user_state("user4", ConversationState.IDLE)
        
        users_in_conversation = manager.get_users_in_conversation()
        
        assert len(users_in_conversation) == 3
        assert "user2" in users_in_conversation
        assert "user3" in users_in_conversation
        assert "user1" not in users_in_conversation
        assert "user4" not in users_in_conversation
    
    def test_cleanup_inactive_users(self):
        """Test cleaning up inactive users."""
        manager = ConversationStateManager()
        
        # Add users with different states
        manager.set_user_state("user1", ConversationState.IDLE)
        manager.set_user_state("user2", ConversationState.IN_CONVERSATION)
        
        # Manually set old activity for user1
        user1_state = manager.get_user_state("user1")
        user1_state.last_activity = datetime.now(timezone.utc) - timedelta(hours=25)
        
        # Cleanup users older than 24 hours
        cleaned_count = manager.cleanup_inactive_users(max_age_hours=24)
        
        assert cleaned_count == 1
        assert "user1" not in manager._user_states
        assert "user2" in manager._user_states


if __name__ == "__main__":
    pytest.main([__file__])
