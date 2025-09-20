"""
Preset selection handlers for the Telegram bot.
"""

import logging
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from ..keyboards.presets import (
    create_preset_selection_keyboard,
    create_preset_info_keyboard,
    create_preset_examples_keyboard,
    create_topic_confirmation_keyboard,
    get_preset_emoji,
    get_preset_display_name,
    get_preset_description,
    get_preset_examples
)

logger = logging.getLogger(__name__)


async def show_presets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show available presets with inline keyboard.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            await update.message.reply_text("❌ Bot not properly initialized. Please try again later.")
            return
        
        # Get available presets
        presets = adapter.get_available_presets()
        
        if not presets:
            await update.message.reply_text(
                "❌ No presets available. Please check your AgentryLab configuration.\n\n"
                "Make sure you have presets in your AgentryLab presets directory."
            )
            return
        
        # Get preset information
        preset_info = {}
        for preset_id in presets:
            try:
                info = adapter.get_preset_info(preset_id)
                preset_info[preset_id] = {
                    'display_name': get_preset_display_name(preset_id),
                    'description': get_preset_description(preset_id),
                    'emoji': get_preset_emoji(preset_id),
                    'category': info.get('category', 'Other'),
                    'examples': get_preset_examples(preset_id)
                }
            except Exception as e:
                logger.warning(f"Could not get info for preset {preset_id}: {e}")
                preset_info[preset_id] = {
                    'display_name': get_preset_display_name(preset_id),
                    'description': get_preset_description(preset_id),
                    'emoji': get_preset_emoji(preset_id),
                    'category': 'Other',
                    'examples': get_preset_examples(preset_id)
                }
        
        # Create keyboard
        keyboard = create_preset_selection_keyboard(presets, preset_info)
        
        # Create message
        message = "🎭 **Choose a Conversation Type:**\n\n"
        message += "Select a preset to start a multi-agent conversation:\n\n"
        
        # Add preset descriptions
        for preset_id in presets:
            info = preset_info[preset_id]
            message += f"{info['emoji']} **{info['display_name']}**\n"
            message += f"_{info['description']}_\n\n"
        
        message += "Click on a preset below to get started!"
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing presets: {e}")
        await update.message.reply_text(
            "❌ Error retrieving presets. Please try again later."
        )


async def handle_preset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle preset selection callbacks.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    query = update.callback_query
    await query.answer()
    
    try:
        data = query.data
        
        if data.startswith("preset_"):
            # Show preset information
            preset_id = data.replace("preset_", "")
            await show_preset_info(query, context, preset_id)
            
        elif data.startswith("select_"):
            # Select preset and ask for topic
            preset_id = data.replace("select_", "")
            await start_topic_input(query, context, preset_id)
            
        elif data.startswith("examples_"):
            # Show preset examples
            preset_id = data.replace("examples_", "")
            await show_preset_examples(query, context, preset_id)
            
        elif data.startswith("example_"):
            # Use example topic
            preset_id = data.replace("example_", "")
            await use_example_topic(query, context, preset_id)
            
        elif data.startswith("custom_"):
            # Enter custom topic
            preset_id = data.replace("custom_", "")
            await start_custom_topic_input(query, context, preset_id)
            
        elif data.startswith("start_"):
            # Start conversation with topic
            preset_id = data.replace("start_", "")
            await start_conversation(query, context, preset_id)
            
        elif data.startswith("edit_"):
            # Edit topic
            preset_id = data.replace("edit_", "")
            await start_custom_topic_input(query, context, preset_id)
            
        elif data == "back_to_presets":
            # Go back to preset selection
            await show_presets_callback(query, context)
            
        elif data == "preset_info":
            # Show general preset information
            await show_general_preset_info(query, context)
            
        elif data == "cancel":
            # Cancel operation
            await query.edit_message_text("❌ Operation cancelled.")
            
        else:
            await query.edit_message_text("❌ Unknown action. Please try again.")
            
    except Exception as e:
        logger.error(f"Error handling preset callback: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")


async def show_preset_info(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Show detailed information about a preset.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    try:
        # Get preset information
        display_name = get_preset_display_name(preset_id)
        description = get_preset_description(preset_id)
        emoji = get_preset_emoji(preset_id)
        examples = get_preset_examples(preset_id)
        
        # Create message
        message = f"{emoji} **{display_name}**\n\n"
        message += f"_{description}_\n\n"
        message += "**Example Topics:**\n"
        for i, example in enumerate(examples[:3], 1):
            message += f"{i}. {example}\n"
        
        if len(examples) > 3:
            message += f"... and {len(examples) - 3} more examples\n"
        
        message += "\nClick below to select this preset or see more examples."
        
        # Create keyboard
        keyboard = create_preset_info_keyboard(preset_id)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing preset info: {e}")
        await query.edit_message_text("❌ Error showing preset information.")


async def show_preset_examples(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Show examples for a preset.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    try:
        # Get preset information
        display_name = get_preset_display_name(preset_id)
        emoji = get_preset_emoji(preset_id)
        examples = get_preset_examples(preset_id)
        
        # Create message
        message = f"{emoji} **{display_name} - Examples**\n\n"
        message += "**Choose an example topic or enter your own:**\n\n"
        
        for i, example in enumerate(examples, 1):
            message += f"{i}. {example}\n"
        
        message += "\nClick on an example to use it, or enter a custom topic."
        
        # Create keyboard
        keyboard = create_preset_examples_keyboard(preset_id)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing preset examples: {e}")
        await query.edit_message_text("❌ Error showing preset examples.")


async def use_example_topic(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Use an example topic for the preset.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    try:
        # Get preset information
        display_name = get_preset_display_name(preset_id)
        emoji = get_preset_emoji(preset_id)
        examples = get_preset_examples(preset_id)
        
        # Use first example as default
        topic = examples[0] if examples else "General discussion"
        
        # Create message
        message = f"{emoji} **{display_name}**\n\n"
        message += f"**Topic:** {topic}\n\n"
        message += "Ready to start the conversation? Click below to begin!"
        
        # Create keyboard
        keyboard = create_topic_confirmation_keyboard(preset_id, topic)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
        # Store topic in context for conversation start
        context.user_data['selected_preset'] = preset_id
        context.user_data['selected_topic'] = topic
        
    except Exception as e:
        logger.error(f"Error using example topic: {e}")
        await query.edit_message_text("❌ Error using example topic.")


async def start_custom_topic_input(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Start custom topic input for a preset.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    try:
        # Get preset information
        display_name = get_preset_display_name(preset_id)
        emoji = get_preset_emoji(preset_id)
        examples = get_preset_examples(preset_id)
        
        # Create message
        message = f"{emoji} **{display_name}**\n\n"
        message += "**Enter your topic:**\n\n"
        message += "Type your topic below. For example:\n"
        for example in examples[:2]:
            message += f"• {example}\n"
        
        message += "\nJust type your message and send it!"
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown'
        )
        
        # Set state for topic input
        context.user_data['waiting_for_topic'] = True
        context.user_data['selected_preset'] = preset_id
        
    except Exception as e:
        logger.error(f"Error starting custom topic input: {e}")
        await query.edit_message_text("❌ Error starting topic input.")


async def start_conversation(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Start a conversation with the selected preset and topic.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    try:
        # Get topic from context
        topic = context.user_data.get('selected_topic')
        if not topic:
            await query.edit_message_text("❌ No topic selected. Please try again.")
            return
        
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            await query.edit_message_text("❌ Bot not properly initialized. Please try again later.")
            return
        
        # Start conversation
        user_id = str(query.from_user.id)
        
        # Show starting message
        display_name = get_preset_display_name(preset_id)
        emoji = get_preset_emoji(preset_id)
        
        message = f"{emoji} **Starting {display_name}...**\n\n"
        message += f"**Topic:** {topic}\n\n"
        message += "⏳ Setting up agents...\n"
        message += "🔄 Initializing conversation...\n\n"
        message += "The conversation will start shortly!"
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown'
        )
        
        # Start the conversation (this will be implemented in conversation handler)
        # For now, just show a placeholder
        await query.message.reply_text(
            "🚀 **Conversation started!**\n\n"
            "This feature will be implemented in the next step.\n"
            "The conversation will be displayed here in real-time.",
            parse_mode='Markdown'
        )
        
        # Clear user data
        context.user_data.pop('waiting_for_topic', None)
        context.user_data.pop('selected_preset', None)
        context.user_data.pop('selected_topic', None)
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await query.edit_message_text("❌ Error starting conversation. Please try again.")


async def show_presets_callback(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show presets from a callback query.
    
    Args:
        query: Callback query object
        context: Bot context
    """
    try:
        # Get adapter from context
        adapter = context.bot_data.get('adapter')
        if not adapter:
            await query.edit_message_text("❌ Bot not properly initialized. Please try again later.")
            return
        
        # Get available presets
        presets = adapter.get_available_presets()
        
        if not presets:
            await query.edit_message_text(
                "❌ No presets available. Please check your AgentryLab configuration."
            )
            return
        
        # Get preset information
        preset_info = {}
        for preset_id in presets:
            try:
                info = adapter.get_preset_info(preset_id)
                preset_info[preset_id] = {
                    'display_name': get_preset_display_name(preset_id),
                    'description': get_preset_description(preset_id),
                    'emoji': get_preset_emoji(preset_id),
                    'category': info.get('category', 'Other'),
                    'examples': get_preset_examples(preset_id)
                }
            except Exception as e:
                logger.warning(f"Could not get info for preset {preset_id}: {e}")
                preset_info[preset_id] = {
                    'display_name': get_preset_display_name(preset_id),
                    'description': get_preset_description(preset_id),
                    'emoji': get_preset_emoji(preset_id),
                    'category': 'Other',
                    'examples': get_preset_examples(preset_id)
                }
        
        # Create keyboard
        keyboard = create_preset_selection_keyboard(presets, preset_info)
        
        # Create message
        message = "🎭 **Choose a Conversation Type:**\n\n"
        message += "Select a preset to start a multi-agent conversation:"
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing presets from callback: {e}")
        await query.edit_message_text("❌ Error retrieving presets. Please try again later.")


async def show_general_preset_info(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show general information about presets.
    
    Args:
        query: Callback query object
        context: Bot context
    """
    try:
        message = "ℹ️ **About Presets**\n\n"
        message += "Presets are pre-configured conversation types that define:\n\n"
        message += "• **Agents**: AI characters with specific roles\n"
        message += "• **Scheduler**: How agents take turns\n"
        message += "• **Prompts**: Instructions for each agent\n"
        message += "• **Tools**: Available tools and resources\n\n"
        message += "Each preset is designed for a specific type of conversation, "
        message += "from debates to therapy sessions to brainstorming.\n\n"
        message += "Click on a preset above to see more details and examples!"
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing general preset info: {e}")
        await query.edit_message_text("❌ Error showing preset information.")
