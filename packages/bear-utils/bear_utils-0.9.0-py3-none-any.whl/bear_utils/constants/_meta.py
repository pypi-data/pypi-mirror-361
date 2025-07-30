from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Self, TextIO


@dataclass(frozen=True)
class Value:
    """A frozen dataclass for holding constant values."""

    value: int
    text: str


class RichIntEnum(IntEnum):
    """Base class for IntEnums with rich metadata."""

    text: str

    def __new__(cls, value: Value) -> Self:
        _value: int = value.value
        text: str = value.text
        obj: Self = int.__new__(cls, _value)
        obj._value_ = _value
        obj.text = text
        return obj

    def __int__(self) -> int:
        """Return the integer value of the enum."""
        return self.value

    def __str__(self) -> str:
        return f"{self.name} ({self.value}): {self.text}"

    @classmethod
    def get(cls, value: Any) -> Self:
        """Try to get an enum member by its value, name, or text."""
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls.from_int(value)
        if isinstance(value, str):
            return cls.from_name(value)
        raise ValueError(f"Cannot convert {value} to {cls.__name__}")

    @classmethod
    def from_name(cls, name: str) -> Self:
        """Convert a string name to its corresponding enum member."""
        try:
            return cls[name.upper()]
        except KeyError as e:
            raise ValueError(f"Name {name} not found in {cls.__name__}") from e

    @classmethod
    def from_int(cls, code: int) -> Self:
        for item in cls:
            if item.value == code:
                return item
        raise ValueError(f"Value {code} not found in {cls.__name__}")

    @classmethod
    def int_to_text(cls, code: int) -> str:
        """Convert an integer to its text representation."""
        try:
            return cls.from_int(code).text
        except ValueError:
            return "Unknown value"


class MockTextIO(TextIO):
    """A mock TextIO class that does nothing."""

    def __init__(self) -> None:
        """Initialize the mock TextIO."""
        self._buffer = []

    def write(self, _s: str, *_) -> None:  # type: ignore[override]
        """Mock write method that appends to the buffer."""
        if _s == "\n":
            return
        self._buffer.append(_s)

    def output_buffer(self) -> list[str]:
        """Get the output buffer."""
        return self._buffer

    def clear(self) -> None:
        """Clear the output buffer."""
        self._buffer.clear()

    def flush(self) -> None:
        """Mock flush method that does nothing."""


class NullFile(TextIO):
    """A class that acts as a null file, discarding all writes."""

    def write(self, _s: str, *_: Any) -> None:  # type: ignore[override]
        """Discard the string written to this null file."""

    def flush(self) -> None:
        """Flush the null file (no operation)."""

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        """Exit context manager (no operation)."""
