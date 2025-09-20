"""
Integration tests for the Telegram bot.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from telegram import Update, User, Message, Chat, CallbackQuery

from bot.main import (
    start_command,
    help_command,
    presets_command,
    status_command,
    pause_command,
    resume_command,
    stop_command,
    handle_message,
    handle_callback_query,
    setup_handlers
)
from bot.handlers import presets, conversation
from bot.states.conversation import ConversationStateManager, ConversationState


class TestBotIntegration:
    """Test bot integration with mocked components."""
    
    @pytest.fixture
    def mock_update(self):
        """Create a mock update object."""
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456789
        update.effective_user.username = "testuser"
        update.effective_user.first_name = "Test"
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock context object."""
        context = Mock()
        context.bot_data = {
            'adapter': Mock(),
            'state_manager': ConversationStateManager()
        }
        context.user_data = {}
        return context
    
    @pytest.fixture
    def mock_callback_query(self):
        """Create a mock callback query object."""
        query = Mock(spec=CallbackQuery)
        query.from_user = Mock(spec=User)
        query.from_user.id = 123456789
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        query.message = Mock(spec=Message)
        query.message.reply_text = AsyncMock()
        return query
    
    @pytest.fixture
    def mock_callback_update(self, mock_callback_query):
        """Create a mock update with callback query."""
        update = Mock(spec=Update)
        update.callback_query = mock_callback_query
        return update


class TestCommandIntegration(TestBotIntegration):
    """Test command integration."""
    
    @pytest.mark.asyncio
    async def test_start_command_integration(self, mock_update, mock_context):
        """Test start command integration."""
        # Mock adapter methods
        mock_context.bot_data['adapter'].get_available_presets.return_value = ["debates", "therapy"]
        mock_context.bot_data['adapter'].get_preset_info.return_value = {
            'display_name': 'Test Preset',
            'description': 'Test description',
            'emoji': '🤖',
            'category': 'Test'
        }
        
        await start_command(mock_update, mock_context)
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        
        # Verify state was reset
        user_state = mock_context.bot_data['state_manager'].get_user_state("123456789")
        assert user_state.state == ConversationState.IDLE
    
    @pytest.mark.asyncio
    async def test_help_command_integration(self, mock_update, mock_context):
        """Test help command integration."""
        await help_command(mock_update, mock_context)
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        
        # Check that help message contains expected commands
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "/start" in call_args
        assert "/help" in call_args
        assert "/presets" in call_args
        assert "/status" in call_args
        assert "/pause" in call_args
        assert "/resume" in call_args
        assert "/stop" in call_args
    
    @pytest.mark.asyncio
    async def test_presets_command_integration(self, mock_update, mock_context):
        """Test presets command integration."""
        # Mock the presets.show_presets function
        with patch('bot.main.presets.show_presets') as mock_show_presets:
            mock_show_presets.return_value = AsyncMock()
            
            await presets_command(mock_update, mock_context)
            
            # Verify show_presets was called
            mock_show_presets.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_status_command_integration(self, mock_update, mock_context):
        """Test status command integration."""
        # Set up user state
        state_manager = mock_context.bot_data['state_manager']
        state_manager.set_user_state("123456789", ConversationState.SELECTING_PRESET)
        state_manager.set_user_preset("123456789", "debates")
        state_manager.set_user_topic("123456789", "Test topic")
        
        await status_command(mock_update, mock_context)
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        
        # Check that status message contains expected information
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Conversation Status" in call_args
        assert "debates" in call_args
        assert "Test topic" in call_args
    
    @pytest.mark.asyncio
    async def test_status_command_no_active_conversation(self, mock_update, mock_context):
        """Test status command with no active conversation."""
        await status_command(mock_update, mock_context)
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        
        # Check that message indicates no active conversation
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "no active conversations" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_pause_command_integration(self, mock_update, mock_context):
        """Test pause command integration."""
        # Mock the conversation.pause_conversation function
        with patch('bot.main.conversation.pause_conversation') as mock_pause:
            mock_pause.return_value = AsyncMock()
            
            await pause_command(mock_update, mock_context)
            
            # Verify pause_conversation was called
            mock_pause.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_resume_command_integration(self, mock_update, mock_context):
        """Test resume command integration."""
        # Mock the conversation.resume_conversation function
        with patch('bot.main.conversation.resume_conversation') as mock_resume:
            mock_resume.return_value = AsyncMock()
            
            await resume_command(mock_update, mock_context)
            
            # Verify resume_conversation was called
            mock_resume.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_stop_command_integration(self, mock_update, mock_context):
        """Test stop command integration."""
        # Mock the conversation.stop_conversation function
        with patch('bot.main.conversation.stop_conversation') as mock_stop:
            mock_stop.return_value = AsyncMock()
            
            await stop_command(mock_update, mock_context)
            
            # Verify stop_conversation was called
            mock_stop.assert_called_once_with(mock_update, mock_context)


class TestMessageIntegration(TestBotIntegration):
    """Test message handling integration."""
    
    @pytest.mark.asyncio
    async def test_handle_message_integration(self, mock_update, mock_context):
        """Test message handling integration."""
        # Mock the conversation.handle_topic_input function
        with patch('bot.main.conversation.handle_topic_input') as mock_handle:
            mock_handle.return_value = AsyncMock()
            
            await handle_message(mock_update, mock_context)
            
            # Verify handle_topic_input was called
            mock_handle.assert_called_once_with(mock_update, mock_context)


class TestCallbackIntegration(TestBotIntegration):
    """Test callback handling integration."""
    
    @pytest.mark.asyncio
    async def test_handle_callback_query_integration(self, mock_callback_update, mock_context):
        """Test callback query handling integration."""
        # Mock the presets.handle_preset_callback function
        with patch('bot.main.presets.handle_preset_callback') as mock_handle:
            mock_handle.return_value = AsyncMock()
            
            await handle_callback_query(mock_callback_update, mock_context)
            
            # Verify handle_preset_callback was called
            mock_handle.assert_called_once_with(mock_callback_update, mock_context)


class TestPresetHandlerIntegration(TestBotIntegration):
    """Test preset handler integration."""
    
    @pytest.mark.asyncio
    async def test_show_presets_integration(self, mock_update, mock_context):
        """Test show presets integration."""
        # Mock adapter methods
        mock_adapter = mock_context.bot_data['adapter']
        mock_adapter.get_available_presets.return_value = ["debates", "therapy"]
        mock_adapter.get_preset_info.return_value = {
            'display_name': 'Test Preset',
            'description': 'Test description',
            'emoji': '🤖',
            'category': 'Test'
        }
        
        await presets.show_presets(mock_update, mock_context)
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        
        # Check that presets message contains expected content
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Choose a Conversation Type" in call_args
        assert "debates" in call_args.lower()
        assert "therapy" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_show_presets_no_presets(self, mock_update, mock_context):
        """Test show presets with no available presets."""
        # Mock adapter to return empty presets
        mock_adapter = mock_context.bot_data['adapter']
        mock_adapter.get_available_presets.return_value = []
        
        await presets.show_presets(mock_update, mock_context)
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        
        # Check that error message is shown
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "No presets available" in call_args
    
    @pytest.mark.asyncio
    async def test_handle_preset_callback_integration(self, mock_callback_update, mock_context):
        """Test preset callback handling integration."""
        # Set up callback data
        mock_callback_update.callback_query.data = "preset_debates"
        
        # Mock adapter methods
        mock_adapter = mock_context.bot_data['adapter']
        mock_adapter.get_available_presets.return_value = ["debates"]
        mock_adapter.get_preset_info.return_value = {
            'display_name': 'Debates',
            'description': 'Structured debates',
            'emoji': '⚖️',
            'category': 'Discussion'
        }
        
        await presets.handle_preset_callback(mock_callback_update, mock_context)
        
        # Verify callback was answered
        mock_callback_update.callback_query.answer.assert_called_once()
        
        # Verify message was edited
        mock_callback_update.callback_query.edit_message_text.assert_called_once()


class TestConversationHandlerIntegration(TestBotIntegration):
    """Test conversation handler integration."""
    
    @pytest.mark.asyncio
    async def test_handle_topic_input_integration(self, mock_update, mock_context):
        """Test topic input handling integration."""
        # Set up user data for topic input
        mock_context.user_data['waiting_for_topic'] = True
        mock_context.user_data['selected_preset'] = 'debates'
        mock_update.message.text = "Should remote work become the standard?"
        
        # Mock the conversation.start_conversation_with_agentrylab function
        with patch('bot.handlers.conversation.start_conversation_with_agentrylab') as mock_start:
            mock_start.return_value = AsyncMock(return_value="test-conversation-id")
            
            await conversation.handle_topic_input(mock_update, mock_context)
            
            # Verify reply_text was called
            mock_update.message.reply_text.assert_called_once()
            
            # Check that confirmation message was sent
            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "debates" in call_args
            assert "Should remote work become the standard?" in call_args
    
    @pytest.mark.asyncio
    async def test_handle_topic_input_invalid_topic(self, mock_update, mock_context):
        """Test topic input handling with invalid topic."""
        # Set up user data for topic input
        mock_context.user_data['waiting_for_topic'] = True
        mock_context.user_data['selected_preset'] = 'debates'
        mock_update.message.text = "Hi"  # Too short
        
        await conversation.handle_topic_input(mock_update, mock_context)
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        
        # Check that error message was sent
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "3 characters" in call_args
    
    @pytest.mark.asyncio
    async def test_handle_regular_message_integration(self, mock_update, mock_context):
        """Test regular message handling integration."""
        # Set up user not waiting for topic input
        mock_context.user_data['waiting_for_topic'] = False
        mock_update.message.text = "Hello bot"
        
        await conversation.handle_regular_message(mock_update, mock_context)
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        
        # Check that help message was sent
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Hello!" in call_args
        assert "/start" in call_args


class TestStateManagerIntegration(TestBotIntegration):
    """Test state manager integration."""
    
    def test_state_manager_integration(self, mock_context):
        """Test state manager integration with bot context."""
        state_manager = mock_context.bot_data['state_manager']
        
        # Test user state management
        user_id = "123456789"
        
        # Initially idle
        assert state_manager.can_user_start_conversation(user_id)
        
        # Set selecting preset
        state_manager.set_user_state(user_id, ConversationState.SELECTING_PRESET)
        assert state_manager.is_user_active(user_id)
        assert not state_manager.is_user_in_conversation(user_id)
        
        # Set in conversation
        state_manager.set_user_state(user_id, ConversationState.IN_CONVERSATION)
        assert state_manager.is_user_in_conversation(user_id)
        
        # Reset state
        state_manager.reset_user_state(user_id)
        assert state_manager.can_user_start_conversation(user_id)
    
    def test_multiple_users_state_management(self, mock_context):
        """Test state management with multiple users."""
        state_manager = mock_context.bot_data['state_manager']
        
        # Add multiple users
        state_manager.set_user_state("user1", ConversationState.IDLE)
        state_manager.set_user_state("user2", ConversationState.SELECTING_PRESET)
        state_manager.set_user_state("user3", ConversationState.IN_CONVERSATION)
        
        # Test active users
        active_users = state_manager.get_active_users()
        assert len(active_users) == 2
        assert "user2" in active_users
        assert "user3" in active_users
        assert "user1" not in active_users
        
        # Test users in conversation
        users_in_conversation = state_manager.get_users_in_conversation()
        assert len(users_in_conversation) == 1
        assert "user3" in users_in_conversation


class TestErrorHandlingIntegration(TestBotIntegration):
    """Test error handling integration."""
    
    @pytest.mark.asyncio
    async def test_adapter_error_handling(self, mock_update, mock_context):
        """Test error handling when adapter fails."""
        # Mock adapter to raise exception
        mock_adapter = mock_context.bot_data['adapter']
        mock_adapter.get_available_presets.side_effect = Exception("Adapter error")
        
        await presets.show_presets(mock_update, mock_context)
        
        # Verify error message was sent
        mock_update.message.reply_text.assert_called_once()
        
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Error retrieving presets" in call_args
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self, mock_update, mock_context):
        """Test error handling for validation errors."""
        # Set up invalid topic input
        mock_context.user_data['waiting_for_topic'] = True
        mock_context.user_data['selected_preset'] = 'debates'
        mock_update.message.text = ""  # Empty topic
        
        await conversation.handle_topic_input(mock_update, mock_context)
        
        # Verify error message was sent
        mock_update.message.reply_text.assert_called_once()
        
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "empty" in call_args.lower()


if __name__ == "__main__":
    pytest.main([__file__])
