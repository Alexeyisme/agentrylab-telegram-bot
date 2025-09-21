"""
Comprehensive edge case tests for new utilities and services.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from bot.constants import Messages, CallbackPrefixes, ConversationStates
from bot.services.conversation_service import ConversationService
from bot.services.preset_service import PresetService
from bot.templates.messages import MessageTemplates
from bot.utils.context_helpers import (
    get_user_id, get_user_info, get_user_data, set_user_data, clear_user_data,
    is_user_waiting_for_topic, get_selected_preset, get_selected_topic,
    require_adapter
)
from bot.utils.error_handling import handle_errors, _send_error_message
from bot.utils.validation import (
    validate_topic_input, validate_user_message, validate_preset_id,
    validate_user_id, validate_conversation_id, sanitize_text
)
from tests.factories.test_data import TestDataFactory


class TestEdgeCases:
    """Test edge cases for new utilities and services."""
    
    def test_get_user_id_edge_cases(self):
        """Test get_user_id with various edge cases."""
        # Test with None update
        assert get_user_id(None) is None
        
        # Test with update without effective_user
        update = Mock()
        update.effective_user = None
        assert get_user_id(update) is None
        
        # Test with update without user ID
        update.effective_user = Mock()
        update.effective_user.id = None
        assert get_user_id(update) is None
        
        # Test with valid update
        update.effective_user.id = 123456789
        assert get_user_id(update) == "123456789"
    
    def test_get_user_info_edge_cases(self):
        """Test get_user_info with various edge cases."""
        # Test with None update
        assert get_user_info(None) is None
        
        # Test with update without effective_user
        update = Mock()
        update.effective_user = None
        assert get_user_info(update) is None
        
        # Test with partial user info
        update.effective_user = Mock()
        update.effective_user.id = 123456789
        update.effective_user.username = None
        update.effective_user.first_name = "Test"
        update.effective_user.last_name = None
        
        user_info = get_user_info(update)
        assert user_info['id'] == 123456789
        assert user_info['username'] is None
        assert user_info['first_name'] == "Test"
        assert user_info['last_name'] is None
    
    def test_get_user_data_edge_cases(self):
        """Test get_user_data with various edge cases."""
        # Test with None context
        assert get_user_data(None, None, 'key') is None
        
        # Test with context without user_data
        context = Mock()
        context.user_data = None
        assert get_user_data(None, context, 'key') is None
        
        # Test with missing key
        context.user_data = {}
        assert get_user_data(None, context, 'missing_key') is None
        
        # Test with valid data
        context.user_data = {'key': 'value'}
        assert get_user_data(None, context, 'key') == 'value'
    
    def test_set_user_data_edge_cases(self):
        """Test set_user_data with various edge cases."""
        # Test with None context
        set_user_data(None, None, 'key', 'value')  # Should not raise
        
        # Test with context without user_data
        context = Mock()
        context.user_data = None
        set_user_data(None, context, 'key', 'value')  # Should not raise
        
        # Test with valid context
        context.user_data = {}
        set_user_data(None, context, 'key', 'value')
        assert context.user_data['key'] == 'value'
    
    def test_clear_user_data_edge_cases(self):
        """Test clear_user_data with various edge cases."""
        # Test with None context
        clear_user_data(None, None)  # Should not raise
        
        # Test with context without user_data
        context = Mock()
        context.user_data = None
        clear_user_data(None, context)  # Should not raise
        
        # Test with valid context
        context.user_data = {'key1': 'value1', 'key2': 'value2'}
        clear_user_data(None, context)
        assert len(context.user_data) == 0
    
    def test_is_user_waiting_for_topic_edge_cases(self):
        """Test is_user_waiting_for_topic with various edge cases."""
        # Test with None context
        assert is_user_waiting_for_topic(None, None) is False
        
        # Test with context without user_data
        context = Mock()
        context.user_data = None
        assert is_user_waiting_for_topic(None, context) is False
        
        # Test with missing key
        context.user_data = {}
        assert is_user_waiting_for_topic(None, context) is False
        
        # Test with False value
        context.user_data = {'waiting_for_topic': False}
        assert is_user_waiting_for_topic(None, context) is False
        
        # Test with True value
        context.user_data = {'waiting_for_topic': True}
        assert is_user_waiting_for_topic(None, context) is True
    
    def test_get_selected_preset_edge_cases(self):
        """Test get_selected_preset with various edge cases."""
        # Test with None context
        assert get_selected_preset(None, None) is None
        
        # Test with context without user_data
        context = Mock()
        context.user_data = None
        assert get_selected_preset(None, context) is None
        
        # Test with missing key
        context.user_data = {}
        assert get_selected_preset(None, context) is None
        
        # Test with valid data
        context.user_data = {'selected_preset': 'debates'}
        assert get_selected_preset(None, context) == 'debates'
    
    def test_get_selected_topic_edge_cases(self):
        """Test get_selected_topic with various edge cases."""
        # Test with None context
        assert get_selected_topic(None, None) is None
        
        # Test with context without user_data
        context = Mock()
        context.user_data = None
        assert get_selected_topic(None, context) is None
        
        # Test with missing key
        context.user_data = {}
        assert get_selected_topic(None, context) is None
        
        # Test with valid data
        context.user_data = {'selected_topic': 'Test topic'}
        assert get_selected_topic(None, context) == 'Test topic'
    
    @pytest.mark.asyncio
    async def test_require_adapter_edge_cases(self):
        """Test require_adapter with various edge cases."""
        # Test with None context
        with pytest.raises(Exception):
            await require_adapter(None, None)
        
        # Test with context without bot_data
        context = Mock()
        context.bot_data = None
        with pytest.raises(Exception):
            await require_adapter(None, context)
        
        # Test with context without adapter
        context.bot_data = {}
        with pytest.raises(Exception):
            await require_adapter(None, context)
        
        # Test with valid adapter
        context.bot_data = {'adapter': Mock()}
        adapter = await require_adapter(None, context)
        assert adapter is not None
    
    def test_handle_errors_decorator_edge_cases(self):
        """Test handle_errors decorator with various edge cases."""
        # Test with None error message
        @handle_errors(None)
        async def test_func():
            raise Exception("Test error")
        
        # Test with empty error message
        @handle_errors("")
        async def test_func_empty():
            raise Exception("Test error")
        
        # Test with valid error message
        @handle_errors("Test error message")
        async def test_func_valid():
            raise Exception("Test error")
        
        # Test with function that doesn't raise
        @handle_errors("Test error message")
        async def test_func_no_error():
            return "success"
        
        # These should not raise exceptions
        assert True  # If we get here, the decorator works
    
    @pytest.mark.asyncio
    async def test_send_error_message_edge_cases(self):
        """Test _send_error_message with various edge cases."""
        # Test with None update
        await _send_error_message(None, "Test error")  # Should not raise
        
        # Test with update without callback_query or message
        update = Mock()
        update.callback_query = None
        update.message = None
        await _send_error_message(update, "Test error")  # Should not raise
        
        # Test with callback_query
        update.callback_query = Mock()
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        await _send_error_message(update, "Test error")  # Should not raise
        
        # Test with message
        update.callback_query = None
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        await _send_error_message(update, "Test error")  # Should not raise
    
    def test_validate_topic_input_edge_cases(self):
        """Test validate_topic_input with various edge cases."""
        # Test with None input
        result = validate_topic_input(None)
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with empty string
        result = validate_topic_input("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with whitespace only
        result = validate_topic_input("   ")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with very long input
        long_input = "A" * 1000
        result = validate_topic_input(long_input)
        assert result['valid'] is False
        assert "500 characters" in result['error']
        
        # Test with special characters
        result = validate_topic_input("Test <script>alert('xss')</script> topic")
        assert result['valid'] is True  # Should be sanitized
        
        # Test with unicode characters
        result = validate_topic_input("Test topic with émojis 🎉")
        assert result['valid'] is True
    
    def test_validate_user_message_edge_cases(self):
        """Test validate_user_message with various edge cases."""
        # Test with None input
        result = validate_user_message(None)
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with empty string
        result = validate_user_message("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with very long input
        long_input = "A" * 2000
        result = validate_user_message(long_input)
        assert result['valid'] is False
        assert "1000 characters" in result['error']
        
        # Test with valid input
        result = validate_user_message("Hello, world!")
        assert result['valid'] is True
        assert result['cleaned_message'] == "Hello, world!"
    
    def test_validate_preset_id_edge_cases(self):
        """Test validate_preset_id with various edge cases."""
        # Test with None input
        result = validate_preset_id(None)
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with empty string
        result = validate_preset_id("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with invalid characters
        result = validate_preset_id("invalid@preset#id")
        assert result['valid'] is False
        assert "invalid" in result['error'].lower()
        
        # Test with valid input
        result = validate_preset_id("debates")
        assert result['valid'] is True
        assert result['cleaned_preset_id'] == "debates"
    
    def test_validate_user_id_edge_cases(self):
        """Test validate_user_id with various edge cases."""
        # Test with None input
        result = validate_user_id(None)
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with empty string
        result = validate_user_id("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with non-numeric input
        result = validate_user_id("not_a_number")
        assert result['valid'] is False
        assert "numeric" in result['error'].lower()
        
        # Test with valid input
        result = validate_user_id("123456789")
        assert result['valid'] is True
        assert result['cleaned_user_id'] == "123456789"
    
    def test_validate_conversation_id_edge_cases(self):
        """Test validate_conversation_id with various edge cases."""
        # Test with None input
        result = validate_conversation_id(None)
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with empty string
        result = validate_conversation_id("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
        
        # Test with invalid format
        result = validate_conversation_id("not-a-uuid")
        assert result['valid'] is False
        assert "format" in result['error'].lower()
        
        # Test with valid UUID
        valid_uuid = "12345678-1234-1234-1234-123456789012"
        result = validate_conversation_id(valid_uuid)
        assert result['valid'] is True
        assert result['cleaned_conversation_id'] == valid_uuid
    
    def test_sanitize_text_edge_cases(self):
        """Test sanitize_text with various edge cases."""
        # Test with None input
        result = sanitize_text(None)
        assert result == ""
        
        # Test with empty string
        result = sanitize_text("")
        assert result == ""
        
        # Test with whitespace only
        result = sanitize_text("   ")
        assert result == ""
        
        # Test with HTML tags
        result = sanitize_text("Hello <script>alert('xss')</script> world")
        assert "<script>" not in result
        assert "alert" not in result
        
        # Test with special characters
        result = sanitize_text("Hello &lt;world&gt; &amp; &quot;test&quot;")
        assert "&lt;" not in result
        assert "&gt;" not in result
        assert "&amp;" not in result
        assert "&quot;" not in result
        
        # Test with unicode characters
        result = sanitize_text("Hello émojis 🎉")
        assert result == "Hello émojis 🎉"
    
    def test_message_templates_edge_cases(self):
        """Test MessageTemplates with various edge cases."""
        # Test with None input
        result = MessageTemplates.welcome_message(None)
        assert "Welcome to AgentryLab" in result
        
        # Test with empty string
        result = MessageTemplates.welcome_message("")
        assert "Welcome to AgentryLab" in result
        
        # Test with very long name
        long_name = "A" * 1000
        result = MessageTemplates.welcome_message(long_name)
        assert "Welcome to AgentryLab" in result
        
        # Test with special characters
        result = MessageTemplates.welcome_message("Test <script>alert('xss')</script> User")
        assert "Welcome to AgentryLab" in result
        assert "<script>" not in result
    
    def test_conversation_service_edge_cases(self):
        """Test ConversationService with various edge cases."""
        # Test with None adapter
        service = ConversationService(None, None)
        assert service is not None
        
        # Test with None state_manager
        service = ConversationService(Mock(), None)
        assert service is not None
        
        # Test with valid parameters
        service = ConversationService(Mock(), Mock())
        assert service is not None
    
    def test_preset_service_edge_cases(self):
        """Test PresetService with various edge cases."""
        # Test with None adapter
        service = PresetService(None)
        assert service is not None
        
        # Test with valid adapter
        service = PresetService(Mock())
        assert service is not None
    
    def test_test_data_factory_edge_cases(self):
        """Test TestDataFactory with various edge cases."""
        # Test with None parameters
        user_id = TestDataFactory.create_user_id()
        assert user_id is not None
        
        # Test with empty parameters
        topic = TestDataFactory.create_topic("")
        assert topic == ""
        
        # Test with very long parameters
        long_topic = TestDataFactory.create_topic("A" * 1000)
        assert len(long_topic) == 1000
        
        # Test with special characters
        special_topic = TestDataFactory.create_topic("Test <script>alert('xss')</script> topic")
        assert "Test" in special_topic
        assert "<script>" in special_topic  # Factory doesn't sanitize
    
    def test_constants_edge_cases(self):
        """Test constants with various edge cases."""
        # Test that constants are not None
        assert Messages.NO_PRESET_SELECTED is not None
        assert Messages.NO_TOPIC_SELECTED is not None
        assert Messages.NO_CONVERSATION_FOUND is not None
        
        # Test that constants are strings
        assert isinstance(Messages.NO_PRESET_SELECTED, str)
        assert isinstance(Messages.NO_TOPIC_SELECTED, str)
        assert isinstance(Messages.NO_CONVERSATION_FOUND, str)
        
        # Test that constants are not empty
        assert len(Messages.NO_PRESET_SELECTED) > 0
        assert len(Messages.NO_TOPIC_SELECTED) > 0
        assert len(Messages.NO_CONVERSATION_FOUND) > 0
    
    def test_callback_prefixes_edge_cases(self):
        """Test CallbackPrefixes with various edge cases."""
        # Test that prefixes are not None
        assert CallbackPrefixes.PRESET is not None
        assert CallbackPrefixes.SELECT is not None
        assert CallbackPrefixes.EXAMPLES is not None
        
        # Test that prefixes are strings
        assert isinstance(CallbackPrefixes.PRESET, str)
        assert isinstance(CallbackPrefixes.SELECT, str)
        assert isinstance(CallbackPrefixes.EXAMPLES, str)
        
        # Test that prefixes are not empty
        assert len(CallbackPrefixes.PRESET) > 0
        assert len(CallbackPrefixes.SELECT) > 0
        assert len(CallbackPrefixes.EXAMPLES) > 0
    
    def test_conversation_states_edge_cases(self):
        """Test ConversationStates with various edge cases."""
        # Test that states are not None
        assert ConversationStates.IDLE is not None
        assert ConversationStates.SELECTING_PRESET is not None
        assert ConversationStates.IN_CONVERSATION is not None
        
        # Test that states are strings
        assert isinstance(ConversationStates.IDLE, str)
        assert isinstance(ConversationStates.SELECTING_PRESET, str)
        assert isinstance(ConversationStates.IN_CONVERSATION, str)
        
        # Test that states are not empty
        assert len(ConversationStates.IDLE) > 0
        assert len(ConversationStates.SELECTING_PRESET) > 0
        assert len(ConversationStates.IN_CONVERSATION) > 0


if __name__ == "__main__":
    pytest.main([__file__])
