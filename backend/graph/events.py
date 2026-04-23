"""
Per-request event bus for streaming workflow progress to the SSE endpoint.

Usage (backend):
    1. In the SSE generator, create a queue and call `bind_queue(queue, loop)`.
    2. Pass that queue into `asyncio.to_thread(run_query, ..., progress_queue=queue)`.
    3. Nodes call `emit(type, **payload)` – the helper schedules `put_nowait`
       onto the main loop via `call_soon_threadsafe` so it is safe from worker threads.

emit() is a silent no-op when no queue is bound, which keeps tests and
notebook runs working without any changes.
"""

from __future__ import annotations

import asyncio
from contextvars import ContextVar
from typing import Any

# Holds (queue, loop) for the current request, set inside the worker thread
# via run_in_executor before the workflow starts.
_progress_queue: ContextVar[asyncio.Queue | None] = ContextVar(
    "_progress_queue", default=None
)
_progress_loop: ContextVar[asyncio.AbstractEventLoop | None] = ContextVar(
    "_progress_loop", default=None
)


def bind_queue(queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None:
    """Bind the per-request queue and the main event loop into the current context."""
    _progress_queue.set(queue)
    _progress_loop.set(loop)


def emit(event_type: str, **payload: Any) -> None:
    """
    Emit a progress event.  Safe to call from any thread.
    No-op when no queue is bound (tests / CLI / /chat non-stream endpoint).
    """
    queue = _progress_queue.get(None)
    loop = _progress_loop.get(None)
    if queue is None or loop is None:
        return
    event = {"type": event_type, **payload}
    try:
        loop.call_soon_threadsafe(queue.put_nowait, event)
    except Exception:
        pass  # Never crash the workflow because of a missed progress event
