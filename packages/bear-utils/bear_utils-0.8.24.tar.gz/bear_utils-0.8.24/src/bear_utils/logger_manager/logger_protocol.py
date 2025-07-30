"""A protocol for logging classes for general use."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LoggerProtocol(Protocol):
    """A protocol for logging classes."""

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        ...

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        ...

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        ...

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        ...


@runtime_checkable
class AsyncLoggerProtocol(Protocol):
    """A protocol for asynchronous logging classes."""

    async def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message asynchronously."""
        ...

    async def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message asynchronously."""
        ...

    async def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message asynchronously."""
        ...

    async def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message asynchronously."""
        ...
