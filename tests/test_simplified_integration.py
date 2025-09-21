"""
Simplified integration tests for the new architecture.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from telegram import Update, User, Message, Chat, CallbackQuery

from bot.handlers import commands, callbacks, messages
from bot.state import state
from bot.registry import services
from tests.factories.test_data import TestDataFactory


class TestSimplifiedIntegration:
    """Test simplified bot integration."""
    
    @pytest.fixture
    def mock_update(self):
        """Create mock update."""
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456789
        update.effective_user.first_name = "TestUser"
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        update.message.text = "test message"
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock()
        context.bot_data = {
            'adapter': Mock(),
            'state_manager': Mock()
        }
        return context
    
    @pytest.fixture
    def mock_callback_update(self):
        """Create mock callback update."""
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456789
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.data = "select_debates"
        return update
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_update, mock_context):
        """Test start command."""
        with patch('bot.handlers.commands.show_presets') as mock_show_presets:
            await commands.start_command(mock_update, mock_context)
            
            # Verify welcome message was sent
            mock_update.message.reply_text.assert_called()
            # Verify show_presets was called
            mock_show_presets.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_help_command(self, mock_update, mock_context):
        """Test help command."""
        await commands.help_command(mock_update, mock_context)
        
        # Verify help message was sent
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_status_command(self, mock_update, mock_context):
        """Test status command."""
        # Mock user state
        with patch('bot.state.state.get_user_state') as mock_get_state:
            mock_user_state = Mock()
            mock_user_state.state = "idle"
            mock_get_state.return_value = mock_user_state
            
            await commands.status_command(mock_update, mock_context)
            
            # Verify status message was sent
            mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_message(self, mock_update, mock_context):
        """Test message handling."""
        with patch('bot.state.state.get_user_state') as mock_get_state:
            mock_user_state = Mock()
            mock_user_state.state = "idle"
            mock_get_state.return_value = mock_user_state
            
            await messages.handle_message(mock_update, mock_context)
            
            # Verify message was handled
            mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_callback(self, mock_callback_update, mock_context):
        """Test callback handling."""
        await callbacks.handle_callback(mock_callback_update, mock_context)
        
        # Verify callback was answered
        mock_callback_update.callback_query.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_topic_input_handling(self, mock_update, mock_context):
        """Test topic input handling."""
        with patch('bot.state.state.get_user_state') as mock_get_state:
            mock_user_state = Mock()
            mock_user_state.state = "waiting_topic"
            mock_user_state.preset_id = "debates"
            mock_get_state.return_value = mock_user_state
            
            with patch('bot.registry.services.get_conversation_service') as mock_get_service:
                mock_service = Mock()
                mock_service.start_conversation = AsyncMock(return_value="conv_123")
                mock_get_service.return_value = mock_service
                
                await messages.handle_topic_input(mock_update, mock_context, "test topic")
                
                # Verify conversation was started
                mock_service.start_conversation.assert_called_once()
    
    def test_state_management(self):
        """Test state management."""
        # Test getting user state
        user_state = state.get_user_state("123456789")
        assert user_state.user_id == "123456789"
        assert user_state.state == "idle"
        
        # Test setting user state
        state.set_user_state("123456789", "active", conversation_id="conv_123")
        user_state = state.get_user_state("123456789")
        assert user_state.state == "active"
        assert user_state.conversation_id == "conv_123"
        
        # Test clearing user state
        state.clear_user_state("123456789")
        user_state = state.get_user_state("123456789")
        assert user_state.state == "idle"
    
    def test_service_registry(self):
        """Test service registry."""
        # Test initialization
        mock_adapter = Mock()
        mock_state = Mock()
        services.initialize(mock_adapter, mock_state)
        
        assert services.adapter == mock_adapter
        assert services.state_manager == mock_state
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_update, mock_context):
        """Test error handling."""
        # Test with invalid state
        with patch('bot.state.state.get_user_state') as mock_get_state:
            mock_get_state.side_effect = Exception("Test error")
            
            await messages.handle_message(mock_update, mock_context)
            
            # Should not raise exception
            mock_update.message.reply_text.assert_called()
    
    def test_factory_integration(self):
        """Test integration with test data factory."""
        # Test factory data creation
        user_id = TestDataFactory.create_user_id()
        assert isinstance(user_id, str)
        assert len(user_id) > 0
        
        # Test mock update creation
        update = TestDataFactory.create_mock_update()
        assert update.effective_user.id is not None
        
        # Test mock context creation
        context = TestDataFactory.create_mock_context()
        assert context.bot_data is not None
