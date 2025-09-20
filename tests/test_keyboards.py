"""
Tests for keyboard generation.
"""

import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.presets import (
    create_preset_selection_keyboard,
    create_preset_info_keyboard,
    create_preset_examples_keyboard,
    create_topic_confirmation_keyboard,
    get_preset_emoji,
    get_preset_display_name,
    get_preset_description,
    get_preset_examples
)


class TestPresetSelectionKeyboard:
    """Test preset selection keyboard generation."""
    
    def test_create_preset_selection_keyboard(self):
        """Test creating preset selection keyboard."""
        presets = ["debates", "therapy", "brainstorm"]
        preset_info = {
            "debates": {
                "display_name": "Debates",
                "description": "Structured debates",
                "emoji": "⚖️",
                "category": "Discussion"
            },
            "therapy": {
                "display_name": "Therapy",
                "description": "Therapeutic conversations",
                "emoji": "🛋️",
                "category": "Support"
            },
            "brainstorm": {
                "display_name": "Brainstorming",
                "description": "Creative brainstorming",
                "emoji": "💡",
                "category": "Creative"
            }
        }
        
        keyboard = create_preset_selection_keyboard(presets, preset_info)
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0
        
        # Check that preset buttons are present
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        assert "⚖️ Debates" in all_buttons
        assert "🛋️ Therapy" in all_buttons
        assert "💡 Brainstorming" in all_buttons
    
    def test_create_preset_selection_keyboard_empty(self):
        """Test creating keyboard with empty presets."""
        keyboard = create_preset_selection_keyboard([], {})
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Should still have navigation buttons
        assert len(keyboard.inline_keyboard) > 0
    
    def test_create_preset_selection_keyboard_single_preset(self):
        """Test creating keyboard with single preset."""
        presets = ["debates"]
        preset_info = {
            "debates": {
                "display_name": "Debates",
                "description": "Structured debates",
                "emoji": "⚖️",
                "category": "Discussion"
            }
        }
        
        keyboard = create_preset_selection_keyboard(presets, preset_info)
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0


class TestPresetInfoKeyboard:
    """Test preset info keyboard generation."""
    
    def test_create_preset_info_keyboard(self):
        """Test creating preset info keyboard."""
        keyboard = create_preset_info_keyboard("debates")
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Two rows
        
        # Check button texts
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        assert "✅ Select This Preset" in all_buttons
        assert "📝 See Examples" in all_buttons
        assert "🔙 Back to Presets" in all_buttons
        assert "❌ Cancel" in all_buttons


class TestPresetExamplesKeyboard:
    """Test preset examples keyboard generation."""
    
    def test_create_preset_examples_keyboard(self):
        """Test creating preset examples keyboard."""
        keyboard = create_preset_examples_keyboard("debates")
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Two rows
        
        # Check button texts
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        assert "✅ Use This Example" in all_buttons
        assert "✏️ Enter Custom Topic" in all_buttons
        assert "🔙 Back to Preset Info" in all_buttons
        assert "❌ Cancel" in all_buttons


class TestTopicConfirmationKeyboard:
    """Test topic confirmation keyboard generation."""
    
    def test_create_topic_confirmation_keyboard(self):
        """Test creating topic confirmation keyboard."""
        keyboard = create_topic_confirmation_keyboard("debates", "Remote work vs office")
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Two rows
        
        # Check button texts
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        assert "✅ Start Conversation" in all_buttons
        assert "✏️ Edit Topic" in all_buttons
        assert "🔙 Back to Presets" in all_buttons
        assert "❌ Cancel" in all_buttons


class TestPresetHelpers:
    """Test preset helper functions."""
    
    def test_get_preset_emoji(self):
        """Test getting preset emoji."""
        assert get_preset_emoji("debates") == "⚖️"
        assert get_preset_emoji("stand_up") == "🎭"
        assert get_preset_emoji("therapy") == "🛋️"
        assert get_preset_emoji("research") == "🔬"
        assert get_preset_emoji("brainstorm") == "💡"
        assert get_preset_emoji("unknown") == "🤖"  # Default
    
    def test_get_preset_display_name(self):
        """Test getting preset display name."""
        assert get_preset_display_name("debates") == "Debates"
        assert get_preset_display_name("stand_up") == "Stand-up Comedy"
        assert get_preset_display_name("therapy") == "Therapy Session"
        assert get_preset_display_name("unknown_preset") == "Unknown Preset"
    
    def test_get_preset_description(self):
        """Test getting preset description."""
        assert "debate" in get_preset_description("debates").lower()
        assert "comedy" in get_preset_description("stand_up").lower()
        assert "therapy" in get_preset_description("therapy").lower()
        assert "research" in get_preset_description("research").lower()
        assert "brainstorm" in get_preset_description("brainstorm").lower()
    
    def test_get_preset_examples(self):
        """Test getting preset examples."""
        examples = get_preset_examples("debates")
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert all(isinstance(example, str) for example in examples)
        
        # Check that examples contain expected content
        examples_text = " ".join(examples).lower()
        assert "remote work" in examples_text or "artificial intelligence" in examples_text
    
    def test_get_preset_examples_unknown(self):
        """Test getting examples for unknown preset."""
        examples = get_preset_examples("unknown_preset")
        assert isinstance(examples, list)
        assert len(examples) == 1
        assert examples[0] == "General discussion topic"


class TestKeyboardIntegration:
    """Test keyboard integration and callback data."""
    
    def test_callback_data_format(self):
        """Test that callback data is properly formatted."""
        keyboard = create_preset_selection_keyboard(["debates"], {
            "debates": {
                "display_name": "Debates",
                "description": "Structured debates",
                "emoji": "⚖️",
                "category": "Discussion"
            }
        })
        
        # Find the debates button
        debates_button = None
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Debates" in button.text:
                    debates_button = button
                    break
        
        assert debates_button is not None
        assert debates_button.callback_data == "preset_debates"
    
    def test_info_keyboard_callback_data(self):
        """Test preset info keyboard callback data."""
        keyboard = create_preset_info_keyboard("debates")
        
        # Find the select button
        select_button = None
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Select This Preset" in button.text:
                    select_button = button
                    break
        
        assert select_button is not None
        assert select_button.callback_data == "select_debates"
    
    def test_examples_keyboard_callback_data(self):
        """Test preset examples keyboard callback data."""
        keyboard = create_preset_examples_keyboard("debates")
        
        # Find the use example button
        example_button = None
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Use This Example" in button.text:
                    example_button = button
                    break
        
        assert example_button is not None
        assert example_button.callback_data == "example_debates"
    
    def test_confirmation_keyboard_callback_data(self):
        """Test topic confirmation keyboard callback data."""
        keyboard = create_topic_confirmation_keyboard("debates", "Test topic")
        
        # Find the start conversation button
        start_button = None
        for row in keyboard.inline_keyboard:
            for button in row:
                if "Start Conversation" in button.text:
                    start_button = button
                    break
        
        assert start_button is not None
        assert start_button.callback_data == "start_debates"


if __name__ == "__main__":
    pytest.main([__file__])
