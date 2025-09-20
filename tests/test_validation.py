"""
Tests for validation utilities.
"""

import pytest
from bot.utils.validation import (
    validate_topic_input,
    validate_user_message,
    validate_preset_id,
    validate_user_id,
    validate_conversation_id,
    sanitize_text
)


class TestValidateTopicInput:
    """Test topic input validation."""
    
    def test_valid_topic(self):
        """Test valid topic input."""
        result = validate_topic_input("Should remote work become the standard?")
        assert result['valid'] is True
        assert result['error'] is None
        assert result['cleaned_topic'] == "Should remote work become the standard?"
    
    def test_empty_topic(self):
        """Test empty topic input."""
        result = validate_topic_input("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
    
    def test_whitespace_only_topic(self):
        """Test whitespace-only topic input."""
        result = validate_topic_input("   ")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
    
    def test_too_short_topic(self):
        """Test topic that's too short."""
        result = validate_topic_input("Hi")
        assert result['valid'] is False
        assert "3 characters" in result['error']
    
    def test_too_long_topic(self):
        """Test topic that's too long."""
        long_topic = "A" * 501
        result = validate_topic_input(long_topic)
        assert result['valid'] is False
        assert "500 characters" in result['error']
    
    def test_inappropriate_content(self):
        """Test topic with inappropriate content."""
        result = validate_topic_input("How to hack into systems")
        assert result['valid'] is False
        assert "inappropriate" in result['error'].lower()
    
    def test_excessive_repetition(self):
        """Test topic with excessive repetition."""
        repetitive_topic = "work work work work work work work work work work work work"
        result = validate_topic_input(repetitive_topic)
        assert result['valid'] is False
        assert "repetition" in result['error'].lower()
    
    def test_invalid_characters(self):
        """Test topic with invalid characters."""
        result = validate_topic_input("Topic with <script>alert('xss')</script>")
        assert result['valid'] is False
        assert "invalid characters" in result['error'].lower()
    
    def test_valid_with_punctuation(self):
        """Test valid topic with punctuation."""
        result = validate_topic_input("What's the future of AI? Let's discuss!")
        assert result['valid'] is True
        assert result['error'] is None


class TestValidateUserMessage:
    """Test user message validation."""
    
    def test_valid_message(self):
        """Test valid user message."""
        result = validate_user_message("I agree with your point about remote work.")
        assert result['valid'] is True
        assert result['error'] is None
        assert result['cleaned_message'] == "I agree with your point about remote work."
    
    def test_empty_message(self):
        """Test empty message."""
        result = validate_user_message("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
    
    def test_too_long_message(self):
        """Test message that's too long."""
        long_message = "A" * 2001
        result = validate_user_message(long_message)
        assert result['valid'] is False
        assert "2000 characters" in result['error']
    
    def test_inappropriate_content(self):
        """Test message with inappropriate content."""
        result = validate_user_message("This is spam content")
        assert result['valid'] is False
        assert "inappropriate" in result['error'].lower()


class TestValidatePresetId:
    """Test preset ID validation."""
    
    def test_valid_preset_id(self):
        """Test valid preset ID."""
        result = validate_preset_id("debates")
        assert result['valid'] is True
        assert result['error'] is None
        assert result['cleaned_preset_id'] == "debates"
    
    def test_preset_id_with_underscore(self):
        """Test preset ID with underscore."""
        result = validate_preset_id("stand_up_comedy")
        assert result['valid'] is True
        assert result['error'] is None
    
    def test_preset_id_with_hyphen(self):
        """Test preset ID with hyphen."""
        result = validate_preset_id("stand-up-comedy")
        assert result['valid'] is True
        assert result['error'] is None
    
    def test_empty_preset_id(self):
        """Test empty preset ID."""
        result = validate_preset_id("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
    
    def test_invalid_characters(self):
        """Test preset ID with invalid characters."""
        result = validate_preset_id("debates@123")
        assert result['valid'] is False
        assert "invalid characters" in result['error'].lower()
    
    def test_too_long_preset_id(self):
        """Test preset ID that's too long."""
        long_id = "a" * 51
        result = validate_preset_id(long_id)
        assert result['valid'] is False
        assert "50 characters" in result['error']


class TestValidateUserId:
    """Test user ID validation."""
    
    def test_valid_user_id(self):
        """Test valid user ID."""
        result = validate_user_id("123456789")
        assert result['valid'] is True
        assert result['error'] is None
        assert result['cleaned_user_id'] == "123456789"
    
    def test_empty_user_id(self):
        """Test empty user ID."""
        result = validate_user_id("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
    
    def test_non_numeric_user_id(self):
        """Test non-numeric user ID."""
        result = validate_user_id("abc123")
        assert result['valid'] is False
        assert "format" in result['error'].lower()
    
    def test_too_short_user_id(self):
        """Test user ID that's too short."""
        result = validate_user_id("1234")
        assert result['valid'] is False
        assert "length" in result['error'].lower()
    
    def test_too_long_user_id(self):
        """Test user ID that's too long."""
        result = validate_user_id("1234567890123456")
        assert result['valid'] is False
        assert "length" in result['error'].lower()


class TestValidateConversationId:
    """Test conversation ID validation."""
    
    def test_valid_conversation_id(self):
        """Test valid conversation ID."""
        valid_id = "12345678-1234-1234-1234-123456789012"
        result = validate_conversation_id(valid_id)
        assert result['valid'] is True
        assert result['error'] is None
        assert result['cleaned_conversation_id'] == valid_id
    
    def test_empty_conversation_id(self):
        """Test empty conversation ID."""
        result = validate_conversation_id("")
        assert result['valid'] is False
        assert "empty" in result['error'].lower()
    
    def test_invalid_format(self):
        """Test conversation ID with invalid format."""
        result = validate_conversation_id("not-a-uuid")
        assert result['valid'] is False
        assert "format" in result['error'].lower()
    
    def test_case_insensitive(self):
        """Test conversation ID validation is case insensitive."""
        valid_id = "12345678-1234-1234-1234-123456789012".upper()
        result = validate_conversation_id(valid_id)
        assert result['valid'] is True


class TestSanitizeText:
    """Test text sanitization."""
    
    def test_sanitize_whitespace(self):
        """Test whitespace sanitization."""
        result = sanitize_text("  hello   world  ")
        assert result == "hello world"
    
    def test_sanitize_harmful_chars(self):
        """Test removal of harmful characters."""
        result = sanitize_text("Hello <script>alert('xss')</script> world")
        assert result == "Hello scriptalert('xss')/script world"
    
    def test_sanitize_excessive_punctuation(self):
        """Test limiting excessive punctuation."""
        result = sanitize_text("Hello!!!!! How are you???")
        assert result == "Hello!!! How are you???"
    
    def test_sanitize_empty_text(self):
        """Test sanitizing empty text."""
        result = sanitize_text("")
        assert result == ""
    
    def test_sanitize_none(self):
        """Test sanitizing None."""
        result = sanitize_text(None)
        assert result == ""


if __name__ == "__main__":
    pytest.main([__file__])
