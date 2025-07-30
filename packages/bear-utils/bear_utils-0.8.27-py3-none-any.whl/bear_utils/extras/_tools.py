import asyncio
from asyncio.subprocess import PIPE
from collections import deque
from functools import cached_property
import shutil
from typing import TYPE_CHECKING

from rich.console import Console

from bear_utils.cli.shell._base_command import BaseShellCommand as ShellCommand
from bear_utils.cli.shell._base_shell import AsyncShellSession
from bear_utils.extras.platform_utils import OS, get_platform

if TYPE_CHECKING:
    from subprocess import CompletedProcess


class ClipboardManager:
    """A class to manage clipboard operations such as copying, pasting, and clearing.

    This class provides methods to interact with the system clipboard.
    """

    def __init__(self, maxlen: int = 10) -> None:
        """Initialize the ClipboardManager with a maximum history length."""
        self.clipboard_history: deque[str] = deque(maxlen=maxlen)
        self.shell = AsyncShellSession(env={"LANG": "en_US.UTF-8"}, verbose=False)
        self._copy: ShellCommand[str]
        self._paste: ShellCommand[str]

        platform: OS = get_platform()
        match platform:
            case OS.DARWIN:
                self._copy = ShellCommand.adhoc(name="pbcopy")
                self._paste = ShellCommand.adhoc(name="pbpaste")
            case OS.LINUX:
                if shutil.which(cmd="wl-copy") and shutil.which(cmd="wl-paste"):
                    self._copy = ShellCommand.adhoc(name="wl-copy")
                    self._paste = ShellCommand.adhoc(name="wl-paste")
                elif shutil.which(cmd="xclip"):
                    self._copy = ShellCommand.adhoc(name="xclip").sub("-selection", "clipboard")
                    self._paste = ShellCommand.adhoc(name="xclip").sub("-selection", "clipboard").value("-o")
                else:
                    raise RuntimeError("No clipboard command found on Linux")
            case OS.WINDOWS:
                self._copy = ShellCommand.adhoc(name="clip")
                self._paste = ShellCommand.adhoc(name="powershell").sub("Get-Clipboard")
            case _:
                raise RuntimeError(f"Unsupported platform: {platform}")

    def _copy_cmd(self) -> ShellCommand[str]:
        """Get the copy command based on the platform."""
        return self._copy

    def _paste_cmd(self) -> ShellCommand[str]:
        """Get the paste command based on the platform."""
        return self._paste

    def get_history(self) -> deque:
        """Get the clipboard history.

        Returns:
            deque: The history of clipboard entries.
        """
        return self.clipboard_history

    async def copy(self, output: str) -> int:
        """A function that copies the output to the clipboard.

        Args:
            output (str): The output to copy to the clipboard.

        Returns:
            int: The return code of the command.
        """
        await self.shell.run(cmd=self._copy, stdin=PIPE)
        result: CompletedProcess[str] = await self.shell.communicate(stdin=output)
        if result.returncode == 0:
            self.clipboard_history.append(output)  # Only append to history if the copy was successful
        return result.returncode

    async def paste(self) -> str:
        """Paste the output from the clipboard.

        Returns:
            str: The content of the clipboard.

        Raises:
            RuntimeError: If the paste command fails.
        """
        try:
            await self.shell.run(cmd=self._paste)
            result: CompletedProcess[str] = await self.shell.communicate()
        except Exception as e:
            raise RuntimeError(f"Error pasting from clipboard: {e}") from e
        if result.returncode != 0:
            raise RuntimeError(f"{self._paste.cmd} failed with return code {result.returncode}")
        return result.stdout

    async def clear(self) -> int:
        """A function that clears the clipboard.

        Returns:
            int: The return code of the command.
        """
        return await self.copy(output="")


def copy_to_clipboard(output: str) -> int:
    """Copy the output to the clipboard.

    Args:
        output (str): The output to copy to the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(future=clipboard_manager.copy(output))


async def copy_to_clipboard_async(output: str) -> int:
    """Asynchronously copy the output to the clipboard.

    Args:
        output (str): The output to copy to the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.copy(output=output)


def paste_from_clipboard() -> str:
    """Paste the output from the clipboard.

    Returns:
        str: The content of the clipboard.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(future=clipboard_manager.paste())


async def paste_from_clipboard_async() -> str:
    """Asynchronously paste the output from the clipboard.

    Returns:
        str: The content of the clipboard.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.paste()


def clear_clipboard() -> int:
    """Clear the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(clipboard_manager.clear())


async def clear_clipboard_async() -> int:
    """Asynchronously clear the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.clear()


class TextHelper:
    @cached_property
    def local_console(self) -> Console:
        return Console()

    def print_header(
        self,
        title: str,
        top_sep: str = "#",
        left_sep: str = ">",
        right_sep: str = "<",
        bottom_sep: str = "#",
        length: int = 60,
        s1: str = "bold red",
        s2: str = "bold blue",
        return_txt: bool = False,
    ) -> str:
        """Generate a header string with customizable separators for each line.

        Args:
            title: The title text to display
            top_sep: Character(s) for the top separator line
            left_sep: Character(s) for the left side of title line
            right_sep: Character(s) for the right side of title line
            bottom_sep: Character(s) for the bottom separator line
            length: Total width of each line
            s1: Style for the title text
            s2: Style for the entire header block
            return_txt: If True, return the text instead of printing
        """
        # Top line: all top_sep characters
        top_line: str = top_sep * length

        # Bottom line: all bottom_sep characters
        bottom_line: str = bottom_sep * length

        # Title line: left_sep chars + title + right_sep chars
        title_with_spaces = f" {title} "
        styled_title = f"[{s1}]{title}[/{s1}]"

        # Calculate padding needed on each side
        title_length = len(title_with_spaces)
        remaining_space = length - title_length
        left_padding = remaining_space // 2
        right_padding = remaining_space - left_padding

        # Build the title line with different left and right separators
        title_line = (
            (left_sep * left_padding) + title_with_spaces.replace(title, styled_title) + (right_sep * right_padding)
        )

        # Assemble the complete header
        output_text: str = f"\n{top_line}\n{title_line}\n{bottom_line}\n"

        if not return_txt:
            self.local_console.print(output_text, style=s2)
        return output_text


def ascii_header(
    title: str,
    top_sep: str = "#",
    left_sep: str = ">",
    right_sep: str = "<",
    bottom_sep: str = "#",
    length: int = 60,
    style1: str = "bold red",
    style2: str = "bold blue",
    print_out: bool = True,
) -> str:
    """Generate a header string for visual tests.

    Args:
        title (str): The title to display in the header.
        top_sep (str): The character to use for the top separator line. Defaults to '#'.
        left_sep (str): The character to use for the left side of title line. Defaults to '>'.
        right_sep (str): The character to use for the right side of title line. Defaults to '<'.
        bottom_sep (str): The character to use for the bottom separator line. Defaults to '#'.
        length (int): The total length of the header line. Defaults to 60.
        style1 (str): The style for the title text. Defaults to 'bold red'.
        style2 (str): The style for the separator text. Defaults to 'bold blue'.
        print_out (bool): Whether to print the header or just return it. Defaults to True.
    """
    text_helper = TextHelper()
    if print_out:
        text_helper.print_header(
            title=title,
            top_sep=top_sep,
            left_sep=left_sep,
            right_sep=right_sep,
            bottom_sep=bottom_sep,
            length=length,
            s1=style1,
            s2=style2,
            return_txt=False,
        )
        return ""
    return text_helper.print_header(
        title=title,
        top_sep=top_sep,
        left_sep=left_sep,
        right_sep=right_sep,
        bottom_sep=bottom_sep,
        length=length,
        s1=style1,
        s2=style2,
        return_txt=True,
    )


if __name__ == "__main__":
    # Example usage of the TextHelper
    text_helper = TextHelper()
    text_helper.print_header("My Title", top_sep="#", bottom_sep="#")
    text_helper.print_header("My Title", top_sep="=", left_sep=">", right_sep="<", bottom_sep="=")
    text_helper.print_header("My Title", top_sep="-", left_sep="[", right_sep="]", bottom_sep="-")
