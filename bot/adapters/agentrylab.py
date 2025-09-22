"""Extended Telegram adapter with robust streaming support."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncIterator, Dict, Optional

from agentrylab.telegram.adapter import TelegramAdapter
from agentrylab.telegram.models import ConversationEvent, ConversationStatus

_SENTINEL = object()


class AsyncTelegramAdapter(TelegramAdapter):
    """TelegramAdapter variant that tolerates sync Lab.stream generators."""

    def __init__(self, *args: Any, max_workers: int = 4, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._stream_executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="agentrylab-stream",
        )
        self._stream_futures: Dict[str, Any] = {}

    async def _iterate_lab_stream(
        self,
        conversation_id: str,
        lab: Any,
        max_rounds: int,
    ) -> AsyncIterator[Dict[str, Any]]:
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[Any] = asyncio.Queue()

        def producer() -> None:
            try:
                for event in lab.stream(rounds=max_rounds):
                    asyncio.run_coroutine_threadsafe(queue.put(event), loop).result()
            except Exception as exc:  # pragma: no cover - defensive
                asyncio.run_coroutine_threadsafe(queue.put(exc), loop).result()
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(_SENTINEL), loop).result()

        future = self._stream_executor.submit(producer)
        self._stream_futures[conversation_id] = future

        try:
            while True:
                item = await queue.get()
                if item is _SENTINEL:
                    break
                if isinstance(item, Exception):
                    raise item
                yield item
        finally:
            self._stream_futures.pop(conversation_id, None)

    async def _run_conversation(self, conversation_id: str) -> None:  # type: ignore[override]
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
            async for event in self._iterate_lab_stream(
                conversation_id, lab, max_rounds
            ):
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
                        lab.post_user_message(
                            user_msg.content, user_id=user_msg.user_id
                        )
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
            raise
        except Exception as exc:  # pragma: no cover - defensive
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

    def stop_conversation(self, conversation_id: str) -> None:
        super().stop_conversation(conversation_id)
        future = self._stream_futures.pop(conversation_id, None)
        if future:
            future.cancel()

    def cleanup(self) -> None:
        """Shut down the executor gracefully."""
        self._stream_executor.shutdown(wait=False)

    # Ensure executor shuts down if adapter is garbage collected
    def __del__(self) -> None:  # pragma: no cover - defensive cleanup
        try:
            self.cleanup()
        except Exception:  # nosec B110 - defensive cleanup in destructor
            # Log the exception for debugging but don't raise it in destructor
            import logging
            logger = logging.getLogger(__name__)
            logger.debug("Exception during adapter cleanup in destructor", exc_info=True)
