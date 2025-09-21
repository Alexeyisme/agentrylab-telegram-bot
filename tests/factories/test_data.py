"""
Test data factories for creating test objects.

This module provides factories for creating test data objects,
reducing code duplication in tests and improving maintainability.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock

from bot.constants import ConversationStates, EventTypes, Roles, Emojis, PresetCategories
from bot.states.conversation import UserConversationState
# Note: These models are from the AgentryLab core, not the bot
# We'll create mock versions for testing

class MockConversationEvent:
    """Mock conversation event for testing."""
    def __init__(self, conversation_id, event_type, content, metadata=None, agent_id=None, role=None):
        self.conversation_id = conversation_id
        self.event_type = event_type
        self.content = content
        self.metadata = metadata or {}
        self.agent_id = agent_id
        self.role = role

class MockConversationState:
    """Mock conversation state for testing."""
    def __init__(self, conversation_id, preset_id, topic, user_id, status, metadata=None):
        self.conversation_id = conversation_id
        self.preset_id = preset_id
        self.topic = topic
        self.user_id = user_id
        self.status = status
        self.metadata = metadata or {}

class MockConversationStatus:
    """Mock conversation status enum for testing."""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"


class TestDataFactory:
    """Factory for creating test data objects."""
    
    @staticmethod
    def create_user_id(user_id: str = "123456789") -> str:
        """
        Create a test user ID.
        
        Args:
            user_id: User ID string
            
        Returns:
            User ID string
        """
        return user_id
    
    @staticmethod
    def create_conversation_id() -> str:
        """
        Create a test conversation ID.
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def create_preset_id(preset_id: str = "debates") -> str:
        """
        Create a test preset ID.
        
        Args:
            preset_id: Preset ID string
            
        Returns:
            Preset ID string
        """
        return preset_id
    
    @staticmethod
    def create_topic(topic: str = "Should remote work become the standard?") -> str:
        """
        Create a test topic.
        
        Args:
            topic: Topic string
            
        Returns:
            Topic string
        """
        return topic
    
    @staticmethod
    def create_user_conversation_state(
        user_id: str = "123456789",
        state: ConversationStates = ConversationStates.IDLE,
        preset_id: Optional[str] = "debates",
        topic: Optional[str] = "Test topic",
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserConversationState:
        """
        Create a test user conversation state.
        
        Args:
            user_id: User ID
            state: Conversation state
            preset_id: Selected preset ID
            topic: Selected topic
            conversation_id: Conversation ID
            metadata: Additional metadata
            
        Returns:
            UserConversationState instance
        """
        if conversation_id is None:
            conversation_id = TestDataFactory.create_conversation_id()
        
        if metadata is None:
            metadata = {}
        
        return UserConversationState(
            user_id=user_id,
            state=state,
            selected_preset=preset_id,
            selected_topic=topic,
            conversation_id=conversation_id,
            metadata=metadata
        )
    
    @staticmethod
    def create_preset_info(
        preset_id: str = "debates",
        display_name: str = "Debates",
        description: str = "Structured debates with AI agents",
        emoji: str = "⚖️",
        category: str = PresetCategories.DISCUSSION,
        examples: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create test preset information.
        
        Args:
            preset_id: Preset ID
            display_name: Display name
            description: Description
            emoji: Emoji
            category: Category
            examples: List of examples
            
        Returns:
            Preset information dictionary
        """
        if examples is None:
            examples = [
                "Should remote work become the standard?",
                "Is artificial intelligence a threat to humanity?",
                "Should social media be regulated?"
            ]
        
        return {
            'id': preset_id,
            'display_name': display_name,
            'description': description,
            'emoji': emoji,
            'category': category,
            'examples': examples,
            'metadata': {}
        }
    
    @staticmethod
    def create_preset_info_batch(preset_ids: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Create test preset information for multiple presets.
        
        Args:
            preset_ids: List of preset IDs
            
        Returns:
            Dictionary mapping preset IDs to their information
        """
        if preset_ids is None:
            preset_ids = ["debates", "stand_up", "therapy", "research", "brainstorm"]
        
        preset_info = {}
        for preset_id in preset_ids:
            preset_info[preset_id] = TestDataFactory.create_preset_info(preset_id)
        
        return preset_info
    
    @staticmethod
    def create_conversation_event(
        conversation_id: Optional[str] = None,
        event_type: str = EventTypes.AGENT_MESSAGE,
        content: str = "Test message content",
        agent_id: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MockConversationEvent:
        """
        Create a test conversation event.
        
        Args:
            conversation_id: Conversation ID
            event_type: Event type
            content: Event content
            agent_id: Agent ID
            role: Agent role
            metadata: Additional metadata
            
        Returns:
            ConversationEvent instance
        """
        if conversation_id is None:
            conversation_id = TestDataFactory.create_conversation_id()
        
        if metadata is None:
            metadata = {}
        
        return MockConversationEvent(
            conversation_id=conversation_id,
            event_type=event_type,
            content=content,
            metadata=metadata,
            agent_id=agent_id,
            role=role
        )

    @staticmethod
    def create_mock_conversation_event(**kwargs) -> MockConversationEvent:
        """Backward compatible alias for conversation event factory."""
        return TestDataFactory.create_conversation_event(**kwargs)
    
    @staticmethod
    def create_conversation_state(
        conversation_id: Optional[str] = None,
        preset_id: str = "debates",
        topic: str = "Test topic",
        user_id: str = "123456789",
        status: str = MockConversationStatus.ACTIVE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MockConversationState:
        """
        Create a test conversation state.
        
        Args:
            conversation_id: Conversation ID
            preset_id: Preset ID
            topic: Topic
            user_id: User ID
            status: Conversation status
            metadata: Additional metadata
            
        Returns:
            ConversationState instance
        """
        if conversation_id is None:
            conversation_id = TestDataFactory.create_conversation_id()
        
        if metadata is None:
            metadata = {}
        
        return MockConversationState(
            conversation_id=conversation_id,
            preset_id=preset_id,
            topic=topic,
            user_id=user_id,
            status=status,
            metadata=metadata
        )

    @staticmethod
    def create_mock_conversation_state(**kwargs) -> MockConversationState:
        """Backward compatible alias for conversation state factory."""
        return TestDataFactory.create_conversation_state(**kwargs)

    @staticmethod
    def create_mock_conversation_analytics(
        conversation_id: Optional[str] = None,
        preset_id: Optional[str] = None,
        topic: Optional[str] = None,
        user_id: Optional[str] = None,
        total_messages: int = 5,
    ) -> Dict[str, Any]:
        """Create mock analytics data."""
        now = datetime.now(timezone.utc)
        return {
            'conversation_id': conversation_id or TestDataFactory.create_conversation_id(),
            'preset_id': preset_id or TestDataFactory.create_preset_id(),
            'topic': topic or TestDataFactory.create_topic(),
            'user_id': user_id or TestDataFactory.create_user_id(),
            'start_time': now,
            'end_time': now,
            'total_messages': total_messages,
            'user_messages': max(total_messages - 1, 0),
            'agent_messages': max(1, total_messages - 1),
            'status': MockConversationStatus.ACTIVE,
            'duration_seconds': max(total_messages * 3, 1),
            'duration_minutes': max(total_messages // 2, 1),
        }
    
    @staticmethod
    def create_mock_update(
        user_id: str = "123456789",
        username: str = "testuser",
        first_name: str = "Test",
        last_name: str = "User",
        message_text: Optional[str] = None,
        callback_data: Optional[str] = None
    ) -> Mock:
        """
        Create a mock Telegram update object.
        
        Args:
            user_id: User ID
            username: Username
            first_name: First name
            last_name: Last name
            message_text: Message text (if text message)
            callback_data: Callback data (if callback query)
            
        Returns:
            Mock update object
        """
        update = Mock()
        
        # Create mock user
        user = Mock()
        user.id = int(user_id)
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        
        update.effective_user = user
        
        # Create mock message for convenience (even if no text yet)
        message = Mock()
        message.text = message_text
        message.reply_text = AsyncMock()
        update.message = message

        if callback_data:
            # Create mock callback query
            callback_query = Mock()
            callback_query.data = callback_data
            callback_query.from_user = user
            callback_query.answer = AsyncMock()
            callback_query.edit_message_text = AsyncMock()
            callback_query.message = Mock()
            callback_query.message.reply_text = AsyncMock()
            update.callback_query = callback_query
        else:
            update.callback_query = None

        return update
    
    @staticmethod
    def create_mock_context(
        bot_data: Optional[Dict[str, Any]] = None,
        user_data: Optional[Dict[str, Any]] = None
    ) -> Mock:
        """
        Create a mock Telegram context object.
        
        Args:
            bot_data: Bot data dictionary
            user_data: User data dictionary
            
        Returns:
            Mock context object
        """
        context = Mock()
        context.bot_data = bot_data or {}
        context.user_data = user_data or {}
        return context
    
    @staticmethod
    def create_mock_adapter() -> Mock:
        """
        Create a mock AgentryLab adapter.
        
        Returns:
            Mock adapter object
        """
        adapter = Mock()
        
        # Mock adapter methods
        adapter.get_available_presets.return_value = ["debates", "stand_up", "therapy"]
        adapter.get_preset_info.return_value = {"category": "Discussion"}
        adapter.start_conversation.return_value = TestDataFactory.create_conversation_id()
        adapter.pause_conversation.return_value = None
        adapter.resume_conversation.return_value = None
        adapter.stop_conversation.return_value = None
        adapter.post_user_message.return_value = None
        
        # Mock streaming
        async def mock_stream():
            yield TestDataFactory.create_conversation_event()
        
        adapter.stream_events.return_value = mock_stream()
        
        return adapter
    
    @staticmethod
    def create_validation_result(
        valid: bool = True,
        error: Optional[str] = None,
        cleaned_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a test validation result.
        
        Args:
            valid: Whether validation passed
            error: Error message if validation failed
            cleaned_data: Cleaned data if validation passed
            
        Returns:
            Validation result dictionary
        """
        result = {
            'valid': valid,
            'error': error
        }
        
        if valid and cleaned_data:
            result['cleaned_topic'] = cleaned_data
        elif valid:
            result['cleaned_message'] = cleaned_data
        
        return result
    
    @staticmethod
    def create_keyboard_markup(buttons: Optional[List[List[str]]] = None) -> Mock:
        """
        Create a mock inline keyboard markup.
        
        Args:
            buttons: List of button rows
            
        Returns:
            Mock keyboard markup
        """
        if buttons is None:
            buttons = [["Button 1", "Button 2"], ["Button 3"]]
        
        markup = Mock()
        markup.inline_keyboard = buttons
        return markup
    
    @staticmethod
    def create_error_response(
        error_type: str = "general",
        message: str = "An error occurred"
    ) -> Dict[str, Any]:
        """
        Create a test error response.
        
        Args:
            error_type: Type of error
            message: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            'error_type': error_type,
            'message': message,
            'timestamp': datetime.now(timezone.utc)
        }
    
    @staticmethod
    def create_conversation_statistics(
        user_id: str = "123456789",
        conversation_id: Optional[str] = None,
        total_messages: int = 10,
        user_messages: int = 2,
        agent_messages: int = 8
    ) -> Dict[str, Any]:
        """
        Create test conversation statistics.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            total_messages: Total message count
            user_messages: User message count
            agent_messages: Agent message count
            
        Returns:
            Conversation statistics dictionary
        """
        if conversation_id is None:
            conversation_id = TestDataFactory.create_conversation_id()
        
        return {
            'user_id': user_id,
            'conversation_id': conversation_id,
            'started_at': datetime.now(timezone.utc),
            'max_rounds': 10,
            'current_round': 3,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'agent_messages': agent_messages,
            'status': MockConversationStatus.ACTIVE,
            'duration_seconds': 300,
            'duration_minutes': 5
        }
    
    @staticmethod
    def create_preset_summary(
        total_presets: int = 5,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create test preset summary.
        
        Args:
            total_presets: Total number of presets
            categories: List of categories
            
        Returns:
            Preset summary dictionary
        """
        if categories is None:
            categories = ["Discussion", "Entertainment", "Professional"]
        
        return {
            'total_presets': total_presets,
            'categories': categories,
            'presets_by_category': {cat: 2 for cat in categories},
            'most_common_category': categories[0] if categories else None
        }
    
    @staticmethod
    def create_preset_statistics(
        total_presets: int = 5,
        total_categories: int = 3,
        total_examples: int = 25
    ) -> Dict[str, Any]:
        """
        Create test preset statistics.
        
        Args:
            total_presets: Total number of presets
            total_categories: Total number of categories
            total_examples: Total number of examples
            
        Returns:
            Preset statistics dictionary
        """
        return {
            'total_presets': total_presets,
            'total_categories': total_categories,
            'total_examples': total_examples,
            'average_examples_per_preset': round(total_examples / total_presets, 2),
            'most_common_emoji': Emojis.DEFAULT,
            'emoji_distribution': {Emojis.DEFAULT: total_presets},
            'category_distribution': {
                "Discussion": 2,
                "Entertainment": 2,
                "Professional": 1
            }
        }
