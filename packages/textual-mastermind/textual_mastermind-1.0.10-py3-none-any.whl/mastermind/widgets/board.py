from textual.app import ComposeResult
from textual.containers import VerticalScroll

from mastermind.game import Game
from mastermind.widgets.row import Row


class Board(VerticalScroll):
    def __init__(self, game: Game) -> None:
        super().__init__()

        self.game = game

        self.current_row_number = 1
        self.current_row = Row(self.game, row_number=self.current_row_number)

    def compose(self) -> ComposeResult:
        yield self.current_row

    def add_row(self):
        self.current_row_number += 1
        self.current_row = Row(self.game, row_number=self.current_row_number)
        self.mount(self.current_row)
