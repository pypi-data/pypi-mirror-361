import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Callable
from contextlib import suppress
import inspect


def is_async_function(func: Callable) -> bool:
    """Check if a function is asynchronous.

    Args:
        func (Callable): The function/method to check.

    Returns:
        bool: True if the function is asynchronous, False otherwise.
    """
    return inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func) or inspect.isasyncgen(func)


def in_async_loop() -> bool:
    """Check if the current context is already in an async loop.

    Returns:
        bool: True if an async loop is running, False otherwise.
    """
    loop: AbstractEventLoop | None = None
    with suppress(RuntimeError):
        loop = asyncio.get_running_loop()
    return loop.is_running() if loop else False


def gimmie_async_loop() -> AbstractEventLoop:
    """Get the current event loop, creating one if it doesn't exist."""
    if in_async_loop():
        return asyncio.get_event_loop()
    loop: AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop
