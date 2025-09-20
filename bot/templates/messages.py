"""
Message templates for consistent formatting across the bot.

This module provides reusable message templates to reduce code duplication
and ensure consistent formatting across all bot interactions.
"""

from typing import List, Optional
from ..constants import Messages, Emojis


class MessageTemplates:
    """Collection of message templates for consistent formatting."""
    
    @staticmethod
    def welcome_message(user_name: str) -> str:
        """
        Generate welcome message for new users.
        
        Args:
            user_name: User's first name
            
        Returns:
            Formatted welcome message
        """
        return f"""{Messages.WELCOME_TITLE}

{Messages.WELCOME_DESCRIPTION.format(name=user_name)}

{Messages.WELCOME_FEATURES}

{Messages.WELCOME_INSTRUCTIONS}

{Messages.WELCOME_CTA}"""
    
    @staticmethod
    def help_message() -> str:
        """
        Generate help message with all available commands.
        
        Returns:
            Formatted help message
        """
        return f"""{Messages.HELP_TITLE}

{Messages.HELP_GETTING_STARTED}

{Messages.HELP_CONVERSATION_MANAGEMENT}

{Messages.HELP_USAGE}

{Messages.HELP_CONTROLS}

{Messages.HELP_SUPPORT}"""
    
    @staticmethod
    def preset_selection_message() -> str:
        """
        Generate preset selection message.
        
        Returns:
            Formatted preset selection message
        """
        return f"""{Messages.CHOOSE_CONVERSATION_TYPE}

{Messages.SELECT_PRESET_DESCRIPTION}

{Messages.CLICK_PRESET_TO_START}"""
    
    @staticmethod
    def preset_info_message(emoji: str, display_name: str, description: str, examples: List[str]) -> str:
        """
        Generate preset information message.
        
        Args:
            emoji: Preset emoji
            display_name: Preset display name
            description: Preset description
            examples: List of example topics
            
        Returns:
            Formatted preset info message
        """
        message = f"{emoji} **{display_name}**\n\n"
        message += f"_{description}_\n\n"
        message += "**Example Topics:**\n"
        
        for i, example in enumerate(examples[:3], 1):
            message += f"{i}. {example}\n"
        
        if len(examples) > 3:
            message += f"... and {len(examples) - 3} more examples\n"
        
        message += "\nClick below to select this preset or see more examples."
        return message
    
    @staticmethod
    def preset_examples_message(emoji: str, display_name: str, examples: List[str]) -> str:
        """
        Generate preset examples message.
        
        Args:
            emoji: Preset emoji
            display_name: Preset display name
            examples: List of example topics
            
        Returns:
            Formatted preset examples message
        """
        message = f"{emoji} **{display_name} - Examples**\n\n"
        message += "**Choose an example topic or enter your own:**\n\n"
        
        for i, example in enumerate(examples, 1):
            message += f"{i}. {example}\n"
        
        message += "\nClick on an example to use it, or enter a custom topic."
        return message
    
    @staticmethod
    def topic_confirmation_message(emoji: str, display_name: str, topic: str) -> str:
        """
        Generate topic confirmation message.
        
        Args:
            emoji: Preset emoji
            display_name: Preset display name
            topic: Selected topic
            
        Returns:
            Formatted topic confirmation message
        """
        return f"""{emoji} **{display_name}**

**Topic:** {topic}

{Messages.TOPIC_CONFIRMATION_TITLE}"""
    
    @staticmethod
    def topic_input_message(emoji: str, display_name: str, examples: List[str]) -> str:
        """
        Generate topic input message.
        
        Args:
            emoji: Preset emoji
            display_name: Preset display name
            examples: List of example topics
            
        Returns:
            Formatted topic input message
        """
        message = f"{emoji} **{display_name}**\n\n"
        message += f"{Messages.ENTER_TOPIC_TITLE}\n\n"
        message += f"{Messages.ENTER_TOPIC_DESCRIPTION}\n"
        
        for example in examples[:2]:
            message += f"• {example}\n"
        
        message += f"\n{Messages.ENTER_TOPIC_INSTRUCTION}"
        return message
    
    @staticmethod
    def conversation_starting_message(emoji: str, display_name: str, topic: str) -> str:
        """
        Generate conversation starting message.
        
        Args:
            emoji: Preset emoji
            display_name: Preset display name
            topic: Selected topic
            
        Returns:
            Formatted conversation starting message
        """
        return f"""{emoji} **Starting {display_name}...**

**Topic:** {topic}

{Messages.CONVERSATION_SETUP}"""
    
    @staticmethod
    def conversation_started_message() -> str:
        """
        Generate conversation started message.
        
        Returns:
            Formatted conversation started message
        """
        return f"""{Messages.CONVERSATION_STARTED}

{Messages.CONVERSATION_REAL_TIME}

{Messages.CONVERSATION_SEPARATOR}"""
    
    @staticmethod
    def agent_message(role: str, content: str, agent_id: Optional[str] = None) -> str:
        """
        Generate formatted agent message.
        
        Args:
            role: Agent role
            content: Message content
            agent_id: Agent ID (optional)
            
        Returns:
            Formatted agent message
        """
        if role == "user":
            return f"{Emojis.USER} **You:** {content}"
        elif role == "moderator":
            return f"{Emojis.MODERATOR} **Moderator:** {content}"
        elif role == "summarizer":
            return f"{Emojis.SUMMARIZER} **Summarizer:** {content}"
        else:
            agent_name = agent_id or "Agent"
            return f"{Emojis.AGENT} **{agent_name}:** {content}"
    
    @staticmethod
    def user_turn_message() -> str:
        """
        Generate user turn message.
        
        Returns:
            Formatted user turn message
        """
        return f"""{Messages.USER_TURN}

Type your message below:"""
    
    @staticmethod
    def conversation_completed_message() -> str:
        """
        Generate conversation completed message.
        
        Returns:
            Formatted conversation completed message
        """
        return f"""{Messages.CONVERSATION_COMPLETED}

{Messages.CONVERSATION_ENDED}

{Messages.USE_START_COMMAND}"""
    
    @staticmethod
    def conversation_paused_message() -> str:
        """
        Generate conversation paused message.
        
        Returns:
            Formatted conversation paused message
        """
        return f"""{Messages.CONVERSATION_PAUSED}

The conversation has been paused. Use /resume to continue."""
    
    @staticmethod
    def conversation_resumed_message() -> str:
        """
        Generate conversation resumed message.
        
        Returns:
            Formatted conversation resumed message
        """
        return f"""{Messages.CONVERSATION_RESUMED}

The conversation has been resumed. The AI agents will continue."""
    
    @staticmethod
    def conversation_stopped_message() -> str:
        """
        Generate conversation stopped message.
        
        Returns:
            Formatted conversation stopped message
        """
        return f"""{Messages.CONVERSATION_STOPPED}

The conversation has been ended. Use /start to begin a new one."""
    
    @staticmethod
    def message_sent_message() -> str:
        """
        Generate message sent confirmation.
        
        Returns:
            Formatted message sent message
        """
        return f"""{Messages.MESSAGE_SENT}

{Messages.CONVERSATION_INPUT_ADDED} {Messages.CONVERSATION_CONTINUE}"""
    
    @staticmethod
    def waiting_for_turn_message() -> str:
        """
        Generate waiting for turn message.
        
        Returns:
            Formatted waiting for turn message
        """
        return f"""{Messages.WAITING_FOR_TURN}

The AI agents are currently discussing. You'll be prompted when it's your turn!"""
    
    @staticmethod
    def status_message(user_state, preset_info: Optional[dict] = None) -> str:
        """
        Generate user status message.
        
        Args:
            user_state: User conversation state
            preset_info: Preset information (optional)
            
        Returns:
            Formatted status message
        """
        message = f"{Messages.STATUS_TITLE}\n\n"
        message += f"{Messages.STATUS_STATE.format(state=user_state.get_state_description())}\n"
        
        if user_state.selected_preset:
            preset_name = preset_info.get('display_name', user_state.selected_preset) if preset_info else user_state.selected_preset
            message += f"{Messages.STATUS_PRESET.format(preset=preset_name)}\n"
        
        if user_state.selected_topic:
            message += f"{Messages.STATUS_TOPIC.format(topic=user_state.selected_topic)}\n"
        
        if user_state.conversation_id:
            short_id = user_state.conversation_id[:8] + "..."
            message += f"{Messages.STATUS_CONVERSATION_ID.format(conversation_id=short_id)}\n"
        
        last_activity = user_state.last_activity.strftime('%Y-%m-%d %H:%M:%S')
        message += f"{Messages.STATUS_LAST_ACTIVITY.format(last_activity=last_activity)}\n"
        
        return message
    
    @staticmethod
    def no_active_conversation_message() -> str:
        """
        Generate no active conversation message.
        
        Returns:
            Formatted no active conversation message
        """
        return Messages.STATUS_NO_ACTIVE
    
    @staticmethod
    def regular_message_response() -> str:
        """
        Generate response for regular messages when not in conversation.
        
        Returns:
            Formatted regular message response
        """
        return Messages.HELLO_MESSAGE
    
    @staticmethod
    def preset_info_general_message() -> str:
        """
        Generate general preset information message.
        
        Returns:
            Formatted general preset info message
        """
        return Messages.PRESET_INFO_DESCRIPTION
    
    @staticmethod
    def no_presets_available_message() -> str:
        """
        Generate no presets available message.
        
        Returns:
            Formatted no presets available message
        """
        return f"""{Messages.NO_PRESETS_AVAILABLE}

Make sure you have presets in your AgentryLab presets directory."""
    
    @staticmethod
    def error_message(error_type: str = "general") -> str:
        """
        Generate error message based on error type.
        
        Args:
            error_type: Type of error
            
        Returns:
            Formatted error message
        """
        error_messages = {
            "general": Messages.ERROR_OCCURRED,
            "bot_not_initialized": Messages.BOT_NOT_INITIALIZED,
            "no_active_conversation": Messages.NO_ACTIVE_CONVERSATION,
            "no_paused_conversation": Messages.NO_PAUSED_CONVERSATION,
            "no_conversation_to_stop": Messages.NO_CONVERSATION_TO_STOP,
            "no_conversation_to_pause": Messages.NO_CONVERSATION_TO_PAUSE,
            "no_preset_selected": Messages.NO_PRESET_SELECTED,
            "no_topic_selected": Messages.NO_TOPIC_SELECTED,
            "no_conversation_found": Messages.NO_CONVERSATION_FOUND,
            "unknown_action": Messages.UNKNOWN_ACTION,
            "operation_cancelled": Messages.OPERATION_CANCELLED
        }
        
        return error_messages.get(error_type, Messages.ERROR_OCCURRED)
    
    @staticmethod
    def topic_validation_error(error_type: str) -> str:
        """
        Generate topic validation error message.
        
        Args:
            error_type: Type of validation error
            
        Returns:
            Formatted validation error message
        """
        error_messages = {
            "empty": Messages.TOPIC_TOO_SHORT,
            "too_short": Messages.TOPIC_TOO_SHORT,
            "too_long": Messages.TOPIC_TOO_LONG,
            "inappropriate": Messages.TOPIC_INAPPROPRIATE,
            "invalid_chars": Messages.TOPIC_INVALID_CHARS,
            "repetitive": Messages.TOPIC_REPETITIVE
        }
        
        return error_messages.get(error_type, Messages.TOPIC_TOO_SHORT)
    
    @staticmethod
    def connection_error_message() -> str:
        """
        Generate connection error message.
        
        Returns:
            Formatted connection error message
        """
        return f"""❌ **Connection Error**

The conversation connection was lost. 
Please start a new conversation with /start."""
