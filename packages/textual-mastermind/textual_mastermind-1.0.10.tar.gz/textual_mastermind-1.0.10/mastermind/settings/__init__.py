from dataclasses import dataclass, fields
from typing import Any, Final

from textual_utils import _

LANGUAGES: Final[dict[str, str]] = {
    "en": "English",
    "pl": "Polish",
}


@dataclass(frozen=True)
class Variation:
    name: str
    num_rows: int
    num_pegs: int
    num_colors: int

    @property
    def description(self) -> str:
        num_pegs_str = f"{self.num_pegs} pegs"

        return (
            f"{self.name} ({self.num_rows} {_('rows')}, "
            f"{_(num_pegs_str)}, {self.num_colors} {_('colors')})"
        )


VARIATIONS: Final[dict[str, Variation]] = {
    "original": Variation(name="original", num_rows=10, num_pegs=4, num_colors=6),
    "mini": Variation(name="mini", num_rows=6, num_pegs=4, num_colors=6),
    "super": Variation(name="super", num_rows=12, num_pegs=5, num_colors=8),
}


@dataclass
class Settings:
    language: str = "en"
    variation: Variation = VARIATIONS["original"]
    duplicate_colors: bool = False
    blank_color: bool = False

    def set(self, settings_dict: dict[str, Any]) -> None:
        for field in fields(self):
            if field.name == "variation":
                setattr(self, field.name, VARIATIONS[settings_dict[field.name]])
                continue

            setattr(self, field.name, settings_dict[field.name])


app_settings: Settings = Settings()
