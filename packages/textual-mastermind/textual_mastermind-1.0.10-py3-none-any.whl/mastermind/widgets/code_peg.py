import dataclasses

from textual.binding import Binding
from textual.widgets import Select
from textual.widgets._select import SelectOverlay

from mastermind.constants import BLANK_COLOR, CODE_PEG_COLORS
from mastermind.game import Game


class CodePeg(Select[int]):
    def __init__(self, game: Game) -> None:
        self.game = game

        super().__init__(
            options=zip(CODE_PEG_COLORS, range(1, self.game.num_colors + 1)),
            prompt=BLANK_COLOR,
            classes="code_peg",
        )

    def on_mount(self) -> None:
        option_list = self.query_one(SelectOverlay)

        esc_binding: Binding = option_list._bindings.key_to_bindings["escape"][0]
        option_list._bindings.key_to_bindings["escape"] = [
            dataclasses.replace(esc_binding, show=False)
        ]
