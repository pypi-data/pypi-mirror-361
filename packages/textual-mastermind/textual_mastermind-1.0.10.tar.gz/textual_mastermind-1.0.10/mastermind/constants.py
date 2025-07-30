from pathlib import Path
from typing import Final

from textual.binding import Binding
from textual_utils import AppMetadata

APP_METADATA = AppMetadata(
    name="Master Mind",
    version="1.0.9",
    codename="🔴 ⚪",
    author="Rafal Padkowski",
    email="rafaelp@poczta.onet.pl",
)

ICON: Final[str] = "❔"

LOCALEDIR = Path(__file__).parent / "locale"

SETTINGS_PATH: Final[Path] = Path(__file__).parent / "settings" / "settings.toml"

BLANK_COLOR: Final[str] = "⭕"
CODE_PEG_COLORS: Final[list[str]] = ["🔴", "🟢", "🔵", "🟡", "🟣", "🟤", "⚪", "🟠"]
FEEDBACK_PEG_COLORS: Final[list[str]] = ["🔴", "⚪"]

CHECK_DEFAULT_TEXT: Final[str] = "❔"
CHECK_HOVER_TEXT: Final[str] = "❓"

KEY_TO_BINDING: Final[dict[str, Binding]] = {
    "ctrl+q": Binding(
        key="ctrl+q",
        action="quit",
        description="Quit",
        key_display="Ctrl+Q",
        show=True,
    ),
    "ctrl+c": Binding(
        key="ctrl+c",
        action="nothing",
        description="",
    ),
    "f2": Binding(
        key="f2",
        action="new_game",
        description="New game",
        key_display="F2",
    ),
    "f3": Binding(
        key="f3",
        action="settings",
        description="Settings",
        key_display="F3",
    ),
}
