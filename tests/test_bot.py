"""
Basic tests for the Telegram bot.
"""

import pytest
from unittest.mock import Mock, patch
from telegram import Update, User, Message, Chat

class TestBot:
    """Test basic bot functionality."""
    
    def test_config_loading(self):
        """Test that configuration loads correctly."""
        from config import BOT_TOKEN, BOT_USERNAME, POLLING
        
        # These should be loaded from environment or defaults
        assert BOT_TOKEN is not None
        assert BOT_USERNAME is not None
        assert isinstance(POLLING, bool)
    
    @patch('bot.main.adapter')
    def test_start_command(self, mock_adapter):
        """Test the /start command handler."""
        from bot.main import start_command
        
        # Create mock update
        mock_update = Mock(spec=Update)
        mock_user = Mock(spec=User)
        mock_user.id = 12345
        mock_user.username = "testuser"
        mock_user.first_name = "Test"
        mock_update.effective_user = mock_user
        mock_update.message = Mock(spec=Message)
        mock_update.message.reply_text = Mock()
        
        # Mock the async function
        import asyncio
        asyncio.run(start_command(mock_update, None))
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Welcome to AgentryLab" in call_args
        assert "Test" in call_args
    
    @patch('bot.main.adapter')
    def test_help_command(self, mock_adapter):
        """Test the /help command handler."""
        from bot.main import help_command
        
        # Create mock update
        mock_update = Mock(spec=Update)
        mock_update.message = Mock(spec=Message)
        mock_update.message.reply_text = Mock()
        
        # Mock the async function
        import asyncio
        asyncio.run(help_command(mock_update, None))
        
        # Verify reply_text was called
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Available Commands" in call_args
        assert "/start" in call_args
        assert "/help" in call_args

if __name__ == "__main__":
    pytest.main([__file__])
