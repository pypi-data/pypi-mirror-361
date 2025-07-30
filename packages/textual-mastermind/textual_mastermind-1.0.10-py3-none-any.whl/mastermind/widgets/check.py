from textual.widgets import Label

from mastermind.constants import CHECK_DEFAULT_TEXT, CHECK_HOVER_TEXT
from mastermind.game import Game


class Check(Label):
    def __init__(self, game: Game) -> None:
        self.game = game
        self.default_text = (f"{CHECK_DEFAULT_TEXT} " * self.game.num_pegs)[:-1]
        self.hover_text = (f"{CHECK_HOVER_TEXT} " * self.game.num_pegs)[:-1]

        super().__init__(self.default_text, id="check", classes="check")

    def on_enter(self) -> None:
        self.update(self.hover_text)

    def on_leave(self) -> None:
        self.update(self.default_text)
