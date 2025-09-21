"""
Preset selection keyboards for the Telegram bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any, Optional


def create_preset_selection_keyboard(presets: List[str], preset_info: Dict[str, Dict[str, Any]]) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard for preset selection.
    
    Args:
        presets: List of available preset IDs
        preset_info: Dictionary with preset information
        
    Returns:
        InlineKeyboardMarkup with preset selection buttons
    """
    keyboard = []
    
    # Group presets by category if available
    categories = {}
    uncategorized = []
    
    for preset_id in presets:
        info = preset_info.get(preset_id, {})
        category = info.get('category', 'Other')
        
        if category not in categories:
            categories[category] = []
        categories[category].append((preset_id, info))
    
    # Create keyboard rows
    for category, preset_list in categories.items():
        # Add category header if multiple categories
        if len(categories) > 1:
            keyboard.append([InlineKeyboardButton(f"📁 {category}", callback_data="category_header")])
        
        # Add preset buttons (2 per row)
        for i in range(0, len(preset_list), 2):
            row = []
            for j in range(2):
                if i + j < len(preset_list):
                    preset_id, info = preset_list[i + j]
                    emoji = info.get('emoji', '🤖')
                    display_name = info.get('display_name', preset_id.replace('_', ' ').title())
                    button_text = f"{emoji} {display_name}"
                    row.append(InlineKeyboardButton(button_text, callback_data=f"select_{preset_id}"))
            keyboard.append(row)
    
    # Add navigation buttons
    keyboard.append([
        InlineKeyboardButton("ℹ️ Info", callback_data="info_"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def create_preset_info_keyboard(preset_id: str) -> InlineKeyboardMarkup:
    """
    Create a keyboard for preset information display.
    
    Args:
        preset_id: The preset ID
        
    Returns:
        InlineKeyboardMarkup with preset info buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Select This Preset", callback_data=f"select_{preset_id}"),
            InlineKeyboardButton("📝 See Examples", callback_data=f"examples_{preset_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to Presets", callback_data="back_to_presets"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def create_preset_examples_keyboard(preset_id: str) -> InlineKeyboardMarkup:
    """
    Create a keyboard for preset examples.
    
    Args:
        preset_id: The preset ID
        
    Returns:
        InlineKeyboardMarkup with example buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Use This Example", callback_data=f"example_{preset_id}"),
            InlineKeyboardButton("✏️ Enter Custom Topic", callback_data=f"custom_{preset_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to Preset Info", callback_data=f"info_{preset_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def create_topic_confirmation_keyboard(preset_id: str, topic: str) -> InlineKeyboardMarkup:
    """
    Create a keyboard for topic confirmation.
    
    Args:
        preset_id: The preset ID
        topic: The topic text
        
    Returns:
        InlineKeyboardMarkup with confirmation buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Start Conversation", callback_data=f"start_{preset_id}"),
            InlineKeyboardButton("✏️ Edit Topic", callback_data=f"edit_{preset_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to Presets", callback_data="back_to_presets"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_preset_emoji(preset_id: str) -> str:
    """
    Get the appropriate emoji for a preset.
    
    Args:
        preset_id: The preset ID
        
    Returns:
        Emoji string for the preset
    """
    emoji_map = {
        'debates': '⚖️',
        'stand_up': '🎭',
        'therapy': '🛋️',
        'research': '🔬',
        'brainstorm': '💡',
        'negotiation': '🤝',
        'interview': '🎤',
        'storytelling': '📚',
        'teaching': '👨‍🏫',
        'consulting': '💼',
        'default': '🤖'
    }
    
    return emoji_map.get(preset_id.lower(), emoji_map['default'])


def get_preset_display_name(preset_id: str) -> str:
    """
    Get the display name for a preset.
    
    Args:
        preset_id: The preset ID
        
    Returns:
        Display name for the preset
    """
    display_names = {
        'debates': 'Debates',
        'stand_up': 'Stand-up Comedy',
        'therapy': 'Therapy Session',
        'research': 'Research Discussion',
        'brainstorm': 'Brainstorming',
        'negotiation': 'Negotiation Practice',
        'interview': 'Interview Practice',
        'storytelling': 'Storytelling',
        'teaching': 'Teaching Assistant',
        'consulting': 'Consulting Session',
    }
    
    return display_names.get(preset_id.lower(), preset_id.replace('_', ' ').title())


def get_preset_description(preset_id: str) -> str:
    """
    Get the description for a preset.
    
    Args:
        preset_id: The preset ID
        
    Returns:
        Description for the preset
    """
    descriptions = {
        'debates': 'Engage in structured debates with AI agents taking opposing sides on various topics.',
        'stand_up': 'Practice stand-up comedy with AI agents providing feedback and suggestions.',
        'therapy': 'Have therapeutic conversations with AI agents trained in counseling techniques.',
        'research': 'Conduct research discussions with AI agents to explore complex topics.',
        'brainstorm': 'Generate creative ideas through collaborative brainstorming sessions.',
        'negotiation': 'Practice negotiation skills with AI agents in various scenarios.',
        'interview': 'Prepare for interviews with AI agents acting as interviewers.',
        'storytelling': 'Create and develop stories with AI agents as co-writers.',
        'teaching': 'Get help with learning through AI teaching assistants.',
        'consulting': 'Receive consulting advice from AI agents in various domains.',
    }
    
    return descriptions.get(preset_id.lower(), 'A multi-agent conversation with AI agents.')


def get_preset_examples(preset_id: str) -> List[str]:
    """
    Get example topics for a preset.
    
    Args:
        preset_id: The preset ID
        
    Returns:
        List of example topics
    """
    examples = {
        'debates': [
            'Should remote work become the standard?',
            'Is artificial intelligence a threat to humanity?',
            'Should social media be regulated?',
            'Is cryptocurrency the future of money?',
            'Should college education be free?'
        ],
        'stand_up': [
            'Office life and corporate culture',
            'Dating in the modern world',
            'Technology and social media',
            'Family relationships and dynamics',
            'Everyday life observations'
        ],
        'therapy': [
            'Work stress and burnout',
            'Relationship challenges',
            'Anxiety and worry',
            'Life transitions and changes',
            'Self-esteem and confidence'
        ],
        'research': [
            'Climate change and sustainability',
            'Artificial intelligence ethics',
            'Space exploration and colonization',
            'Genetic engineering and biotechnology',
            'Renewable energy technologies'
        ],
        'brainstorm': [
            'New product ideas for a tech startup',
            'Marketing strategies for a local business',
            'Solutions for urban transportation',
            'Innovative educational approaches',
            'Sustainable living practices'
        ],
        'negotiation': [
            'Salary negotiation with employer',
            'Contract terms with client',
            'Real estate purchase agreement',
            'Partnership agreement terms',
            'Service level agreement with vendor'
        ],
        'interview': [
            'Software engineering position',
            'Marketing manager role',
            'Data scientist position',
            'Product manager role',
            'Sales representative position'
        ],
        'storytelling': [
            'Science fiction adventure story',
            'Mystery thriller novel',
            'Fantasy epic tale',
            'Romance novel plot',
            'Historical fiction narrative'
        ],
        'teaching': [
            'Learning Python programming',
            'Understanding machine learning',
            'Studying world history',
            'Mastering mathematics',
            'Improving writing skills'
        ],
        'consulting': [
            'Business strategy development',
            'Digital transformation planning',
            'Market entry strategy',
            'Operational efficiency improvement',
            'Technology adoption roadmap'
        ]
    }
    
    return examples.get(preset_id.lower(), ['General discussion topic'])
