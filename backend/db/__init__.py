import asyncio

from .database import Database
from .seed import seed_database

__all__ = ["Database", "seed_database", "set_main_loop", "run_async"]

_main_loop: asyncio.AbstractEventLoop | None = None


def set_main_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Store the main event loop so that worker threads can schedule coroutines on it."""
    global _main_loop
    _main_loop = loop


def run_async(coro):
    """
    Run an async coroutine from any context (sync or async, main thread or worker thread).

    Uses run_coroutine_threadsafe when a main loop is registered so that the
    asyncpg connection pool (which is bound to the main event loop) is always
    accessed from the correct loop.
    """
    global _main_loop
    if _main_loop is not None and _main_loop.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, _main_loop)
        return future.result()
    # Fallback: no main loop registered (e.g. tests / CLI scripts)
    try:
        loop = asyncio.get_running_loop()
        if not loop.is_running():
            return loop.run_until_complete(coro)
    except RuntimeError:
        pass
    return asyncio.run(coro)
