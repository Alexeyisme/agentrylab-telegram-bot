"""
Preset selection handlers for the Telegram bot.
"""

import logging
from types import SimpleNamespace

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from ..constants import Messages, CallbackPrefixes
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
from ..services.preset_service import PresetService
from ..templates.messages import MessageTemplates
from ..states.conversation import ConversationState
from ..utils.context_helpers import (
    clear_user_data,
    get_state_manager,
    get_user_id,
    require_adapter,
    require_adapter_from_callback,
    set_user_data,
    set_user_data_from_callback,
    set_user_waiting_for_topic,
    set_user_waiting_for_topic_from_callback,
    get_user_id_from_callback,
    clear_user_data_from_callback,
)
from ..utils.error_handling import handle_errors

logger = logging.getLogger(__name__)


@handle_errors("Error retrieving presets. Please try again later.")
async def show_presets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show available presets with inline keyboard.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    adapter = await require_adapter(update, context)
    
    # Create preset service
    preset_service = PresetService(adapter)
    
    # Get available presets
    presets = await preset_service.get_available_presets()
    
    message = update.message
    if not message:
        return
    
    if not presets:
        await message.reply_text(MessageTemplates.no_presets_available_message())
        return
    
    # Get preset information using service
    preset_info = await preset_service.get_preset_info_batch(presets)
    
    # Create keyboard
    keyboard = create_preset_selection_keyboard(presets, preset_info)
    
    # Create message using template
    message_text = MessageTemplates.preset_selection_message()
    
    # Add preset descriptions
    for preset_id in presets:
        info = preset_info[preset_id]
        message_text += f"{info['emoji']} **{info['display_name']}**\n"
        message_text += f"_{info['description']}_\n\n"
    
    message_text += "Click on a preset below to get started!"
    
    await message.reply_text(
        message_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

    user_id = get_user_id(update)
    if user_id:
        state_manager = get_state_manager(context)
        state_manager.set_user_state(user_id, ConversationState.SELECTING_PRESET)
        set_user_waiting_for_topic(update, context, False)


async def handle_preset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle preset selection callbacks.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    query = update.callback_query
    if not query:
        return
    
    await query.answer()
    
    try:
        data = query.data
        if not data:
            return
        
        if data.startswith("preset_"):
            # Show preset information
            preset_id = data.replace("preset_", "")
            await show_preset_info(query, context, preset_id)
            
        elif data.startswith("select_"):
            # Select preset and ask for topic
            preset_id = data.replace("select_", "")
            await start_custom_topic_input(query, context, preset_id)
            
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


@handle_errors("Error showing preset information.")
async def show_preset_info(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Show detailed information about a preset.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    # Get adapter using new utility
    adapter = await require_adapter_from_callback(query, context)
    
    # Create preset service
    preset_service = PresetService(adapter)
    
    # Get preset information using service
    preset_info = await preset_service.get_preset_info(preset_id)
    
    # Create message using template
    message = MessageTemplates.preset_info_message(
        emoji=preset_info['emoji'],
        display_name=preset_info['display_name'],
        description=preset_info['description'],
        examples=preset_info['examples']
    )
    
    # Create keyboard
    keyboard = create_preset_info_keyboard(preset_id)
    
    await query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


@handle_errors("Error showing preset examples.")
async def show_preset_examples(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Show examples for a preset.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    # Get adapter using new utility
    adapter = await require_adapter_from_callback(query, context)
    
    # Create preset service
    preset_service = PresetService(adapter)
    
    # Get preset information using service
    preset_info = await preset_service.get_preset_info(preset_id)
    
    # Create message using template
    message = MessageTemplates.preset_examples_message(
        emoji=preset_info['emoji'],
        display_name=preset_info['display_name'],
        examples=preset_info['examples']
    )
    
    # Create keyboard
    keyboard = create_preset_examples_keyboard(preset_id)
    
    await query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


@handle_errors("Error using example topic.")
async def use_example_topic(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Use an example topic for the preset.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    # Get adapter using new utility
    adapter = await require_adapter_from_callback(query, context)
    
    # Create preset service
    preset_service = PresetService(adapter)
    
    # Get preset information using service
    preset_info = await preset_service.get_preset_info(preset_id)
    
    # Use first example as default
    examples = preset_info['examples']
    topic = examples[0] if examples else "General discussion"
    
    # Create message using template
    message = MessageTemplates.topic_confirmation_message(
        emoji=preset_info['emoji'],
        display_name=preset_info['display_name'],
        topic=topic
    )
    
    # Create keyboard
    keyboard = create_topic_confirmation_keyboard(preset_id, topic)
    
    await query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    
    # Store topic in context for conversation start
    set_user_data_from_callback(query, context, 'selected_preset', preset_id)
    set_user_data_from_callback(query, context, 'selected_topic', topic)

    user_id = get_user_id_from_callback(query)
    if user_id:
        state_manager = get_state_manager(context)
        state_manager.set_user_state(user_id, ConversationState.CONFIRMING_TOPIC)
        state_manager.set_user_preset(user_id, preset_id)
        state_manager.set_user_topic(user_id, topic)
    set_user_waiting_for_topic_from_callback(query, context, False)


@handle_errors("Error starting topic input.")
async def start_custom_topic_input(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Start custom topic input for a preset.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    # Get adapter using new utility
    adapter = await require_adapter_from_callback(query, context)
    
    # Create preset service
    preset_service = PresetService(adapter)
    
    # Get preset information using service
    preset_info = await preset_service.get_preset_info(preset_id)
    
    # Create message using template
    message = MessageTemplates.topic_input_message(
        emoji=preset_info['emoji'],
        display_name=preset_info['display_name'],
        examples=preset_info['examples']
    )
    
    await query.edit_message_text(
        message,
        parse_mode='Markdown'
    )
    
    # Set state for topic input
    set_user_data_from_callback(query, context, 'selected_preset', preset_id)
    set_user_waiting_for_topic_from_callback(query, context, True)

    user_id = get_user_id_from_callback(query)
    if user_id:
        state_manager = get_state_manager(context)
        state_manager.set_user_preset(user_id, preset_id)
        state_manager.set_user_state(user_id, ConversationState.ENTERING_TOPIC)


@handle_errors("Error starting conversation. Please try again.")
async def start_conversation(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, preset_id: str) -> None:
    """
    Start a conversation with the selected preset and topic.
    
    Args:
        query: Callback query object
        context: Bot context
        preset_id: The preset ID
    """
    # Get topic from context
    if not context or not context.user_data:
        return
    
    topic = context.user_data.get('selected_topic')
    if not topic:
        await query.edit_message_text(Messages.NO_TOPIC_SELECTED)
        return
    
    # Get adapter using new utility (also validates bot initialization)
    adapter = await require_adapter_from_callback(query, context)

    # Create preset service to populate display text
    preset_service = PresetService(adapter)
    preset_info = await preset_service.get_preset_info(preset_id)

    start_message = MessageTemplates.conversation_starting_message(
        emoji=preset_info['emoji'],
        display_name=preset_info['display_name'],
        topic=topic
    )
    await query.edit_message_text(start_message, parse_mode='Markdown')

    # Kick off the actual conversation flow using the conversation handlers
    from . import conversation as conversation_handlers
    mock_update = SimpleNamespace(
        message=query.message,
        callback_query=query,
        effective_user=query.from_user,
        effective_chat=query.message.chat if query.message else None,
    )

    conversation_id = await conversation_handlers.start_conversation_with_agentrylab(
        mock_update,
        context,
        preset_id,
        topic,
    )

    set_user_waiting_for_topic_from_callback(query, context, False)
    clear_user_data_from_callback(query, context)


@handle_errors("Error retrieving presets. Please try again later.")
async def show_presets_callback(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show presets from a callback query.
    
    Args:
        query: Callback query object
        context: Bot context
    """
    # Get adapter using new utility
    adapter = await require_adapter_from_callback(query, context)
    
    # Create preset service
    preset_service = PresetService(adapter)
    
    # Get available presets
    presets = await preset_service.get_available_presets()
    
    if not presets:
        await query.edit_message_text(MessageTemplates.no_presets_available_message())
        return
    
    # Get preset information using service
    preset_info = await preset_service.get_preset_info_batch(presets)
    
    # Create keyboard
    keyboard = create_preset_selection_keyboard(presets, preset_info)
    
    # Create message using template
    message = MessageTemplates.preset_selection_message()
    
    await query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


@handle_errors("Error showing preset information.")
async def show_general_preset_info(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show general information about presets.
    
    Args:
        query: Callback query object
        context: Bot context
    """
    # Create message using template
    message = MessageTemplates.preset_info_general_message()
    
    await query.edit_message_text(
        message,
        parse_mode='Markdown'
    )
