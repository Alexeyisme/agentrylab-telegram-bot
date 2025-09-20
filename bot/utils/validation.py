"""
Input validation utilities for the Telegram bot.
"""

import re
from typing import Dict, Any


def validate_topic_input(topic: str) -> Dict[str, Any]:
    """
    Validate topic input from users.
    
    Args:
        topic: The topic text to validate
        
    Returns:
        Dictionary with validation result
    """
    if not topic:
        return {
            'valid': False,
            'error': 'Topic cannot be empty.'
        }
    
    # Check minimum length after stripping
    topic_stripped = topic.strip()
    if len(topic_stripped) < 3:
        return {
            'valid': False,
            'error': 'Topic cannot be empty.' if len(topic_stripped) == 0 else 'Topic must be at least 3 characters long.'
        }
    
    # Check maximum length
    if len(topic) > 500:
        return {
            'valid': False,
            'error': 'Topic is too long. Please keep it under 500 characters.'
        }
    
    # Check for inappropriate content (basic check)
    inappropriate_patterns = [
        r'\b(spam|scam|phishing|malware|virus)\b',
        r'\b(hack|crack|exploit|breach)\b',
        r'\b(illegal|unlawful|criminal)\b',
        r'\b(hate|discrimination|racism|sexism)\b',
        r'\b(violence|threat|harm|kill|murder)\b',
        r'\b(drug|narcotic|addiction|overdose)\b',
        r'\b(terrorism|bomb|weapon|attack)\b'
    ]
    
    topic_lower = topic.lower()
    for pattern in inappropriate_patterns:
        if re.search(pattern, topic_lower):
            return {
                'valid': False,
                'error': 'Topic contains inappropriate content. Please choose a different topic.'
            }
    
    # Check for excessive repetition
    words = topic.split()
    if len(words) > 10:
        word_counts = {}
        for word in words:
            word_lower = word.lower()
            word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
        
        # Check if any word appears more than 30% of the time
        max_repetition = max(word_counts.values()) if word_counts else 0
        if max_repetition > len(words) * 0.3:
            return {
                'valid': False,
                'error': 'Topic contains too much repetition. Please be more specific.'
            }
    
    # Check for valid characters (basic check) - allow apostrophes
    if not re.match(r'^[a-zA-Z0-9\s\.,!?\-_()\']+$', topic):
        return {
            'valid': False,
            'error': 'Topic contains invalid characters. Please use only letters, numbers, and basic punctuation.'
        }
    
    return {
        'valid': True,
        'error': None,
        'cleaned_topic': topic.strip()
    }


def validate_user_message(message: str) -> Dict[str, Any]:
    """
    Validate user message input during conversations.
    
    Args:
        message: The message text to validate
        
    Returns:
        Dictionary with validation result
    """
    if not message:
        return {
            'valid': False,
            'error': 'Message cannot be empty.'
        }
    
    # Check minimum length
    if len(message.strip()) < 1:
        return {
            'valid': False,
            'error': 'Message must contain at least one character.'
        }
    
    # Check maximum length
    if len(message) > 2000:
        return {
            'valid': False,
            'error': 'Message is too long. Please keep it under 2000 characters.'
        }
    
    # Check for inappropriate content (same as topic validation)
    inappropriate_patterns = [
        r'\b(spam|scam|phishing|malware|virus)\b',
        r'\b(hack|crack|exploit|breach)\b',
        r'\b(illegal|unlawful|criminal)\b',
        r'\b(hate|discrimination|racism|sexism)\b',
        r'\b(violence|threat|harm|kill|murder)\b',
        r'\b(drug|narcotic|addiction|overdose)\b',
        r'\b(terrorism|bomb|weapon|attack)\b'
    ]
    
    message_lower = message.lower()
    for pattern in inappropriate_patterns:
        if re.search(pattern, message_lower):
            return {
                'valid': False,
                'error': 'Message contains inappropriate content. Please rephrase your message.'
            }
    
    return {
        'valid': True,
        'error': None,
        'cleaned_message': message.strip()
    }


def validate_preset_id(preset_id: str) -> Dict[str, Any]:
    """
    Validate preset ID.
    
    Args:
        preset_id: The preset ID to validate
        
    Returns:
        Dictionary with validation result
    """
    if not preset_id:
        return {
            'valid': False,
            'error': 'Preset ID cannot be empty.'
        }
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', preset_id):
        return {
            'valid': False,
            'error': 'Preset ID contains invalid characters. Only letters, numbers, underscores, and hyphens are allowed.'
        }
    
    # Check length
    if len(preset_id) > 50:
        return {
            'valid': False,
            'error': 'Preset ID is too long. Please keep it under 50 characters.'
        }
    
    return {
        'valid': True,
        'error': None,
        'cleaned_preset_id': preset_id.strip()
    }


def validate_user_id(user_id: str) -> Dict[str, Any]:
    """
    Validate user ID.
    
    Args:
        user_id: The user ID to validate
        
    Returns:
        Dictionary with validation result
    """
    if not user_id:
        return {
            'valid': False,
            'error': 'User ID cannot be empty.'
        }
    
    # Check if it's a valid Telegram user ID (numeric)
    if not re.match(r'^\d+$', user_id):
        return {
            'valid': False,
            'error': 'Invalid user ID format.'
        }
    
    # Check length (Telegram user IDs are typically 9-10 digits)
    if len(user_id) < 5 or len(user_id) > 15:
        return {
            'valid': False,
            'error': 'User ID length is invalid.'
        }
    
    return {
        'valid': True,
        'error': None,
        'cleaned_user_id': user_id.strip()
    }


def sanitize_text(text: str) -> str:
    """
    Sanitize text input by removing potentially harmful content.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>{}[\]\\|`~]', '', text)
    
    # Limit consecutive punctuation
    text = re.sub(r'([.!?]){3,}', r'\1\1\1', text)
    
    return text


def validate_conversation_id(conversation_id: str) -> Dict[str, Any]:
    """
    Validate conversation ID.
    
    Args:
        conversation_id: The conversation ID to validate
        
    Returns:
        Dictionary with validation result
    """
    if not conversation_id:
        return {
            'valid': False,
            'error': 'Conversation ID cannot be empty.'
        }
    
    # Check for valid UUID format (basic check)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, conversation_id, re.IGNORECASE):
        return {
            'valid': False,
            'error': 'Invalid conversation ID format.'
        }
    
    return {
        'valid': True,
        'error': None,
        'cleaned_conversation_id': conversation_id.strip()
    }
