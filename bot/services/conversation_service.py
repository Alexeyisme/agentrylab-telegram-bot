"""
Conversation service for managing conversation lifecycle.

This service handles all business logic related to conversations,
separating it from the presentation layer (handlers).
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from ..constants import ConversationStates, EventTypes, Roles
from ..config import AGENTRYLAB_PRESETS_PATH
from ..states.conversation import ConversationStateManager, UserConversationState
from ..utils.error_handling import BotError, UserNotActiveError, ConversationNotFoundError

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service for managing conversation lifecycle and business logic.
    
    This service handles all conversation-related operations including
    starting, pausing, resuming, stopping, and streaming conversations.
    """
    
    def __init__(self, adapter, state_manager: ConversationStateManager):
        """
        Initialize the conversation service.
        
        Args:
            adapter: AgentryLab Telegram adapter
            state_manager: Conversation state manager
        """
        self.adapter = adapter
        self.state_manager = state_manager
        self._streaming_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_conversation(
        self, 
        user_id: str, 
        preset_id: str, 
        topic: str,
        max_rounds: int = 10
    ) -> str:
        """
        Start a new conversation.
        
        Args:
            user_id: User ID
            preset_id: Preset ID
            topic: Conversation topic
            max_rounds: Maximum number of conversation rounds
            
        Returns:
            Conversation ID
            
        Raises:
            BotError: If conversation cannot be started
        """
        try:
            # Validate user can start conversation
            user_state = self.state_manager.get_user_state(user_id)
            logger.info(f"User {user_id} state: {user_state.state.value}, can_start: {user_state.can_start_new_conversation()}")
            if not user_state.can_start_new_conversation():
                raise UserNotActiveError("User already has an active conversation")
            
            # Update user state
            self.state_manager.set_user_state(user_id, ConversationStates.STARTING_CONVERSATION)
            self.state_manager.set_user_preset(user_id, preset_id)
            self.state_manager.set_user_topic(user_id, topic)

            # Start conversation with AgentryLab
            preset_config = self._resolve_preset_config(preset_id)
            conversation_id = self.adapter.start_conversation(
                preset_id=preset_config,
                topic=topic,
                user_id=user_id
            )
            
            # Update user state with conversation ID
            self.state_manager.set_user_conversation_id(user_id, conversation_id)
            self.state_manager.set_user_state(user_id, ConversationStates.IN_CONVERSATION)
            
            # Set conversation metadata
            self.state_manager.add_user_metadata(user_id, 'max_rounds', max_rounds)
            self.state_manager.add_user_metadata(user_id, 'started_at', datetime.now(timezone.utc))
            
            logger.info(f"Started conversation {conversation_id} for user {user_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error starting conversation for user {user_id}: {e}")
            self.state_manager.set_user_state(user_id, ConversationStates.ERROR)
            raise BotError(f"Failed to start conversation: {e}")

    def _resolve_preset_config(self, preset_id: str) -> str:
        """Resolve a preset identifier into a loadable config path."""
        path_candidate = Path(preset_id)

        if path_candidate.is_file():
            return str(path_candidate)

        # Build possible filenames (debates -> debates.yaml)
        candidate_names = []
        if path_candidate.suffix:
            candidate_names.append(path_candidate.name)
        else:
            candidate_names.append(f"{path_candidate.name}.yaml")
            candidate_names.append(f"{path_candidate.name}.yml")

        # Check relative to provided path
        for name in candidate_names:
            local_candidate = path_candidate.parent / name
            if local_candidate.is_file():
                return str(local_candidate)

        # Check configured presets directory if provided
        if AGENTRYLAB_PRESETS_PATH:
            base = Path(AGENTRYLAB_PRESETS_PATH)
            for name in candidate_names:
                candidate_path = base / name
                if candidate_path.is_file():
                    return str(candidate_path)

        # Fall back to packaged presets
        try:
            from agentrylab import presets as packaged_presets

            for name in candidate_names:
                packaged_path = packaged_presets.path(name)
                if packaged_path and Path(packaged_path).is_file():
                    return str(packaged_path)
        except Exception as exc:
            logger.debug("Failed to resolve packaged preset for %s: %s", preset_id, exc)

        # As a last resort, return the original identifier (adapter will raise)
        return str(preset_id)
    
    async def pause_conversation(self, user_id: str) -> None:
        """
        Pause an active conversation.
        
        Args:
            user_id: User ID
            
        Raises:
            UserNotActiveError: If user has no active conversation
            BotError: If conversation cannot be paused
        """
        try:
            user_state = self.state_manager.get_user_state(user_id)
            
            if not user_state.is_in_conversation():
                raise UserNotActiveError("User has no active conversation to pause")
            
            conversation_id = user_state.conversation_id
            if not conversation_id:
                raise ConversationNotFoundError("No conversation ID found")
            
            # Pause conversation in AgentryLab
            self.adapter.pause_conversation(conversation_id)
            
            # Update user state
            self.state_manager.set_user_state(user_id, ConversationStates.CONVERSATION_PAUSED)
            
            # Cancel streaming task if running
            if conversation_id in self._streaming_tasks:
                self._streaming_tasks[conversation_id].cancel()
                del self._streaming_tasks[conversation_id]
            
            logger.info(f"Paused conversation {conversation_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error pausing conversation for user {user_id}: {e}")
            raise BotError(f"Failed to pause conversation: {e}")
    
    async def resume_conversation(self, user_id: str) -> None:
        """
        Resume a paused conversation.
        
        Args:
            user_id: User ID
            
        Raises:
            UserNotActiveError: If user has no paused conversation
            BotError: If conversation cannot be resumed
        """
        try:
            user_state = self.state_manager.get_user_state(user_id)
            
            if user_state.state != ConversationStates.CONVERSATION_PAUSED:
                raise UserNotActiveError("User has no paused conversation to resume")
            
            conversation_id = user_state.conversation_id
            if not conversation_id:
                raise ConversationNotFoundError("No conversation ID found")
            
            # Resume conversation in AgentryLab
            self.adapter.resume_conversation(conversation_id)
            
            # Update user state
            self.state_manager.set_user_state(user_id, ConversationStates.IN_CONVERSATION)
            
            logger.info(f"Resumed conversation {conversation_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error resuming conversation for user {user_id}: {e}")
            raise BotError(f"Failed to resume conversation: {e}")
    
    async def stop_conversation(self, user_id: str) -> None:
        """
        Stop an active conversation.
        
        Args:
            user_id: User ID
            
        Raises:
            UserNotActiveError: If user has no active conversation
            BotError: If conversation cannot be stopped
        """
        try:
            user_state = self.state_manager.get_user_state(user_id)
            
            if not user_state.is_in_conversation():
                raise UserNotActiveError("User has no active conversation to stop")
            
            conversation_id = user_state.conversation_id
            if not conversation_id:
                raise ConversationNotFoundError("No conversation ID found")
            
            # Stop conversation in AgentryLab
            self.adapter.stop_conversation(conversation_id)
            
            # Update user state
            self.state_manager.set_user_state(user_id, ConversationStates.CONVERSATION_ENDED)
            
            # Cancel streaming task if running
            if conversation_id in self._streaming_tasks:
                self._streaming_tasks[conversation_id].cancel()
                del self._streaming_tasks[conversation_id]
            
            logger.info(f"Stopped conversation {conversation_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error stopping conversation for user {user_id}: {e}")
            raise BotError(f"Failed to stop conversation: {e}")
    
    async def handle_user_input(self, user_id: str, message: str) -> bool:
        """
        Handle user input during an active conversation.
        
        Args:
            user_id: User ID
            message: User message
            
        Returns:
            True if message was processed successfully
            
        Raises:
            UserNotActiveError: If user is not waiting for input
            BotError: If message cannot be processed
        """
        try:
            user_state = self.state_manager.get_user_state(user_id)
            
            if user_state.state != ConversationStates.WAITING_FOR_USER_INPUT:
                raise UserNotActiveError("User is not waiting for input")
            
            conversation_id = user_state.conversation_id
            if not conversation_id:
                raise ConversationNotFoundError("No conversation ID found")
            
            # Post user message to AgentryLab
            self.adapter.post_user_message(conversation_id, message, user_id=user_id)
            
            # Update user state
            self.state_manager.set_user_state(user_id, ConversationStates.IN_CONVERSATION)
            
            logger.info(f"Processed user input for conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling user input for user {user_id}: {e}")
            raise BotError(f"Failed to process user input: {e}")
    
    async def start_conversation_streaming(self, user_id: str, event_handler) -> None:
        """
        Start streaming conversation events.
        
        Args:
            user_id: User ID
            event_handler: Function to handle conversation events
        """
        try:
            user_state = self.state_manager.get_user_state(user_id)
            conversation_id = user_state.conversation_id
            
            if not conversation_id:
                raise ConversationNotFoundError("No conversation ID found")
            
            # Create streaming task
            task = asyncio.create_task(
                self._stream_conversation_events(conversation_id, user_id, event_handler)
            )
            self._streaming_tasks[conversation_id] = task
            
            logger.info(f"Started streaming for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error starting conversation streaming for user {user_id}: {e}")
            raise BotError(f"Failed to start conversation streaming: {e}")
    
    async def _stream_conversation_events(self, conversation_id: str, user_id: str, event_handler) -> None:
        """
        Stream conversation events from AgentryLab.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            event_handler: Function to handle events
        """
        try:
            # Stream events from AgentryLab
            async for event in self.adapter.stream_events(conversation_id):
                # Check if conversation is still active
                user_state = self.state_manager.get_user_state(user_id)
                if not user_state.is_in_conversation():
                    break
                
                # Handle the event
                await self._handle_conversation_event(event, user_id, event_handler)
                
        except asyncio.CancelledError:
            logger.info(f"Conversation streaming cancelled for {conversation_id}")
        except Exception as e:
            logger.error(f"Error streaming conversation events for {conversation_id}: {e}")
            # Update user state to error
            self.state_manager.set_user_state(user_id, ConversationStates.ERROR)
        finally:
            # Clean up streaming task
            if conversation_id in self._streaming_tasks:
                del self._streaming_tasks[conversation_id]
    
    async def _handle_conversation_event(self, event, user_id: str, event_handler) -> None:
        """
        Handle a single conversation event.
        
        Args:
            event: Conversation event from AgentryLab
            user_id: User ID
            event_handler: Function to handle the event
        """
        try:
            # Determine event type
            event_type = event.event_type
            content = event.content
            agent_id = event.agent_id
            role = event.role
            preview = content[:120] + "…" if isinstance(content, str) and len(content) > 120 else content
            logger.debug(
                "Streaming event type=%s role=%s content=%r",
                event_type,
                role,
                preview,
            )
            
            # Handle different event types
            if event_type == EventTypes.CONVERSATION_STARTED:
                await event_handler("conversation_started", content, None, None)
                
            elif event_type == EventTypes.AGENT_MESSAGE:
                # Determine if it's actually a user message
                if role == Roles.USER:
                    event_type = EventTypes.USER_MESSAGE
                elif role == Roles.MODERATOR:
                    event_type = EventTypes.MODERATOR_ACTION
                elif role == Roles.SUMMARIZER:
                    event_type = EventTypes.SUMMARY_UPDATE
                
                if content:
                    await event_handler(event_type, content, agent_id, role)
                
            elif event_type == EventTypes.USER_TURN:
                # Update user state to waiting for input
                self.state_manager.set_user_state(user_id, ConversationStates.WAITING_FOR_USER_INPUT)
                await event_handler(event_type, content, None, None)
                
            elif event_type == EventTypes.CONVERSATION_COMPLETED:
                # Update user state to completed
                self.state_manager.set_user_state(user_id, ConversationStates.CONVERSATION_ENDED)
                await event_handler(event_type, content, None, None)
                
            elif event_type == EventTypes.ERROR:
                # Update user state to error
                self.state_manager.set_user_state(user_id, ConversationStates.ERROR)
                await event_handler(event_type, content, None, None)
                
            else:
                # Unknown event type, pass through
                await event_handler(event_type, content, agent_id, role)
                
        except Exception as e:
            logger.error(f"Error handling conversation event: {e}")
    
    def get_user_conversation_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's conversation status.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with conversation status information
        """
        user_state = self.state_manager.get_user_state(user_id)
        
        return {
            'user_id': user_id,
            'state': user_state.state.value,
            'state_description': user_state.get_state_description(),
            'preset_id': user_state.selected_preset,
            'topic': user_state.selected_topic,
            'conversation_id': user_state.conversation_id,
            'last_activity': user_state.last_activity,
            'is_active': user_state.is_active(),
            'is_in_conversation': user_state.is_in_conversation(),
            'can_start_new': user_state.can_start_new_conversation(),
            'metadata': user_state.metadata
        }
    
    def get_conversation_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get conversation statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with conversation statistics
        """
        user_state = self.state_manager.get_user_state(user_id)
        
        stats = {
            'user_id': user_id,
            'conversation_id': user_state.conversation_id,
            'started_at': user_state.metadata.get('started_at'),
            'max_rounds': user_state.metadata.get('max_rounds', 10),
            'current_round': user_state.metadata.get('current_round', 0),
            'total_messages': user_state.metadata.get('total_messages', 0),
            'user_messages': user_state.metadata.get('user_messages', 0),
            'agent_messages': user_state.metadata.get('agent_messages', 0),
            'status': user_state.state.value
        }
        
        # Calculate duration if conversation started
        if stats['started_at']:
            duration = datetime.now(timezone.utc) - stats['started_at']
            stats['duration_seconds'] = duration.total_seconds()
            stats['duration_minutes'] = duration.total_seconds() / 60
        
        return stats
    
    def cleanup_inactive_conversations(self, max_age_hours: int = 24) -> int:
        """
        Clean up inactive conversations.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of conversations cleaned up
        """
        try:
            # Clean up inactive user states
            cleaned_users = self.state_manager.cleanup_inactive_users(max_age_hours)
            
            # Clean up streaming tasks for inactive conversations
            current_time = datetime.now(timezone.utc)
            from datetime import timedelta
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            inactive_tasks = []
            for conversation_id, task in self._streaming_tasks.items():
                # Check if task is still running and should be cleaned up
                if task.done() or task.cancelled():
                    inactive_tasks.append(conversation_id)
            
            for conversation_id in inactive_tasks:
                del self._streaming_tasks[conversation_id]
            
            logger.info(f"Cleaned up {cleaned_users} inactive users and {len(inactive_tasks)} streaming tasks")
            return cleaned_users + len(inactive_tasks)
            
        except Exception as e:
            logger.error(f"Error cleaning up inactive conversations: {e}")
            return 0
