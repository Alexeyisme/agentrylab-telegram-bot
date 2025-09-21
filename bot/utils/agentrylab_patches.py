"""Runtime patches to smooth over AgentryLab API differences."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from agentrylab.telegram.adapter import TelegramAdapter
from agentrylab.telegram.models import ConversationEvent, ConversationStatus


def _ensure_async_iter(stream: Any) -> AsyncIterator[Any]:
    """Return an async iterator for both sync and async streams."""

    if hasattr(stream, "__aiter__"):
        return stream  # type: ignore[return-value]

    iterator = iter(stream)

    async def _async_iter() -> AsyncIterator[Any]:
        while True:
            try:
                item = await asyncio.to_thread(next, iterator)
            except StopIteration:
                break
            yield item

    return _async_iter()


def patch_telegram_adapter_streaming() -> None:
    """Patch TelegramAdapter to support sync generators from Lab.stream."""

    if getattr(TelegramAdapter, "_agentrylab_stream_patch_applied", False):
        return

    original_run = TelegramAdapter._run_conversation

    async def _run_conversation(self: TelegramAdapter, conversation_id: str) -> None:  # type: ignore[override]
        try:
            state = self._conversations[conversation_id]
            lab = state.lab_instance
            event_queue = self._event_streams[conversation_id]
            user_queue = self._user_message_queues[conversation_id]

            await self._emit_event(
                conversation_id,
                "conversation_started",
                "Conversation started",
            )

            max_rounds = state.metadata.get("max_rounds", 10)
            stream = _ensure_async_iter(lab.stream(rounds=max_rounds))

            async for event in stream:
                if state.status != ConversationStatus.ACTIVE:
                    break

                event_type = event.get("event", "agent_message")
                if event_type == "agent_message":
                    role = event.get("role", "")
                    if role == "user":
                        event_type = "user_message"
                    elif role == "moderator":
                        event_type = "moderator_action"
                    elif role == "summarizer":
                        event_type = "summary_update"

                conv_event = ConversationEvent(
                    conversation_id=conversation_id,
                    event_type=event_type,
                    content=str(event.get("content", "")),
                    metadata=event.get("metadata", {}),
                    iteration=event.get("iter", 0),
                    agent_id=event.get("agent_id"),
                    role=event.get("role"),
                )

                await event_queue.put(conv_event)

                try:
                    user_msg = user_queue.get_nowait()
                    if not user_msg.processed:
                        lab.post_user_message(user_msg.content, user_id=user_msg.user_id)
                        user_msg.processed = True

                        await self._emit_event(
                            conversation_id,
                            "user_message",
                            user_msg.content,
                            metadata={"user_id": user_msg.user_id},
                        )
                except asyncio.QueueEmpty:
                    pass

            await self._emit_event(
                conversation_id,
                "conversation_completed",
                "Conversation completed",
            )
            state.status = ConversationStatus.COMPLETED

        except asyncio.CancelledError:
            state = self._conversations.get(conversation_id)
            if state:
                state.status = ConversationStatus.STOPPED
        except Exception as exc:  # pragma: no cover - defensive logging
            state = self._conversations.get(conversation_id)
            if state:
                state.status = ConversationStatus.ERROR
            await self._emit_event(
                conversation_id,
                "error",
                f"Error: {exc}",
            )
        finally:
            if conversation_id in self._running_tasks:
                del self._running_tasks[conversation_id]

    # Preserve reference to ConversationEvent for convenience
    _run_conversation.ConversationEvent = TelegramAdapter._emit_event.__globals__[  # type: ignore[attr-defined]
        "ConversationEvent"
    ]

    TelegramAdapter._run_conversation = _run_conversation
    TelegramAdapter._agentrylab_stream_patch_applied = True
