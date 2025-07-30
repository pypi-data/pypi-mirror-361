from __future__ import annotations

from dataclasses import dataclass
from io import StringIO

from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from bear_utils.graphics.font._theme import CyberTheme
from bear_utils.graphics.font.block_font import Style
from bear_utils.logger_manager import LogConsole as Console


@dataclass
class HeaderConfig:
    """Configuration for header styling."""

    top_sep: str = "#"
    left_sep: str = ">"
    right_sep: str = "<"
    bottom_sep: str = "#"
    length: int = 60
    title_style: str = "bold red"  # s1
    border_style: str = "bold blue"  # s2 - top/bottom lines
    separator_style: str = "bold green"  # s3 - left/right separators
    overall_style: str = "bold yellow"  # s4
    center_align: bool = True
    return_txt: bool = False
    use_panel: bool = False  # New option!


class TextHelper:
    def _create_separator_line(self, char: str, length: int, style: str) -> Text:
        """Create a styled separator line."""
        return Text(char * length, style=style)

    def _create_title_line_manual(self, title: str, cfg: HeaderConfig) -> Text:
        """Create title line with manual separator padding."""
        title_with_spaces = f" {title} "
        title_length = len(title_with_spaces)
        remaining_space = cfg.length - title_length
        left_padding = remaining_space // 2
        right_padding = remaining_space - left_padding
        title_line = Text()
        title_line.append(cfg.left_sep * left_padding, style=cfg.separator_style)
        title_line.append(f" {title} ", style=cfg.title_style)
        title_line.append(cfg.right_sep * right_padding, style=cfg.separator_style)
        return title_line

    def _create_title_line_rich(self, title: str, cfg: HeaderConfig) -> Text:
        """Create title line using Rich's alignment."""
        styled_title = Text(f" {title} ", style=cfg.title_style)
        title_line = Text()
        title_line.append(cfg.left_sep, style=cfg.separator_style)
        title_line.append(styled_title)
        title_line.append(cfg.right_sep, style=cfg.separator_style)
        return Text.from_markup(str(Align.center(title_line, width=cfg.length)))

    def _create_panel_header(self, title: str, cfg: HeaderConfig) -> Panel:
        """Create header using Rich Panel."""
        return Panel(
            f"[{cfg.title_style}]{title}[/{cfg.title_style}]",
            width=cfg.length,
            border_style=cfg.border_style,
            expand=False,
        )

    def _create_manual_header(self, title: str, cfg: HeaderConfig) -> list[Text]:
        """Create header using manual separator lines."""
        top_line = self._create_separator_line(cfg.top_sep, cfg.length, cfg.border_style)
        bottom_line = self._create_separator_line(cfg.bottom_sep, cfg.length, cfg.border_style)
        title_line = self._create_title_line_manual(title, cfg)

        return [top_line, title_line, bottom_line]

    def print_header(self, title: str, config: HeaderConfig | None = None, **kwargs) -> str:
        """Generate a header string with customizable separators and styling.

        Args:
            title: The title text to display
            config: HeaderConfig object, or None to use defaults
            **kwargs: Override any config values (top_sep, left_sep, etc.)
        """
        local_console = Console()
        cfg = config or HeaderConfig()
        for key, value in kwargs.items():
            if hasattr(cfg, key):
                setattr(cfg, key, value)

        if cfg.use_panel:
            panel: Panel = self._create_panel_header(title, cfg)
            output: Align | Panel = Align.center(panel) if cfg.center_align else panel

            if not cfg.return_txt:
                local_console.print(output, style=cfg.overall_style)

            temp_console = Console(file=StringIO(), width=cfg.length)
            temp_console.print(output, style=cfg.overall_style)
            return temp_console.file.getvalue()

        header_lines = self._create_manual_header(title, cfg)

        if cfg.center_align:
            header_lines = [Align.center(line) for line in header_lines]

        if not cfg.return_txt:
            local_console.print()  # Leading newline
            for line in header_lines:
                local_console.print(line, style=cfg.overall_style)
            local_console.print()  # Trailing newline
        output_lines: list[str] = [str(line) for line in header_lines]
        return "\n" + "\n".join(output_lines) + "\n"

    def quick_header(self, title: str, style: str = "cyberpunk") -> str:
        """Quick header with predefined styles."""
        styles = {
            "cyberpunk": HeaderConfig(
                top_sep=str(Style.SOLID),
                left_sep=str(Style.RIGHT_ARROWS),
                right_sep=str(Style.LEFT_ARROWS),
                bottom_sep=str(Style.SOLID),
                title_style="bold bright_magenta",
                border_style="bright_cyan",
                separator_style="bright_green",
                overall_style="",
                use_panel=False,
            ),
            "panel": HeaderConfig(title_style="bold bright_magenta", border_style="bright_cyan", use_panel=True),
            "classic": HeaderConfig(),  # Uses defaults
            "minimal": HeaderConfig(top_sep="─", left_sep="", right_sep="", bottom_sep="─", separator_style="dim"),
        }

        config = styles.get(style, HeaderConfig())
        return self.print_header(title, config)


def ascii_header(title: str, print_out: bool = True, **kwargs) -> str:
    """Generate a header string for visual tests.

    Args:
        title: The title to display
        print_out: Whether to print or return the header
        **kwargs: Any HeaderConfig parameters (top_sep, length, etc.)
    """
    config = HeaderConfig(return_txt=not print_out, **kwargs)
    text_helper = TextHelper()
    result = text_helper.print_header(title, config)
    return "" if print_out else result


if __name__ == "__main__":
    top = Style.SOLID.text
    bottom = Style.SOLID.text
    left = Style.RIGHT_ARROWS.text
    right = Style.LEFT_ARROWS.text
    ascii_header(
        "Welcome to Bear Utils",
        top_sep=top,
        bottom_sep=bottom,
        left_sep=left,
        right_sep=right,
        title_style=CyberTheme.primary,
        separator_style=CyberTheme.system,
        border_style=CyberTheme.neon_cyan,
        print_out=True,
    )

    from pyfiglet import figlet_format

    ANSI_SHADOW = "ansi_shadow"
    BLOODY = "bloody"
    BANNER_3_D = "banner3-D"
    POISON = "poison"
    ALPHA = "alpha"
    DOOM = "doom"
    DOT_MATRIX = "dotmatrix"
    JAZMINE = "jazmine"
    RAMMSTEIN = "rammstein"
    REVERSE = "reverse"
    DIAGONAL_3D = "3d_diagonal"
    GHOST = "ghost"

    text = figlet_format("BANKER", font="computer")
    print(text)
