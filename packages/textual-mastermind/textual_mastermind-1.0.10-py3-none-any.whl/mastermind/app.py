import dataclasses
from typing import Any

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.events import Click
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, Select, Switch
from textual_utils import (
    AboutHeaderIcon,
    ConfirmScreen,
    SettingRow,
    SettingsScreen,
    _,
    init_translation,
    load_settings,
    mount_about_header_icon,
    save_settings,
    set_translation,
)

from mastermind.constants import (
    APP_METADATA,
    BLANK_COLOR,
    CODE_PEG_COLORS,
    FEEDBACK_PEG_COLORS,
    ICON,
    KEY_TO_BINDING,
    LOCALEDIR,
    SETTINGS_PATH,
)
from mastermind.game import Game
from mastermind.settings import LANGUAGES, VARIATIONS, app_settings
from mastermind.widgets.board import Board


class MastermindApp(App):
    TITLE = "Master Mind"
    CSS_PATH = "styles.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = list(KEY_TO_BINDING.values())

    def __init__(self) -> None:
        super().__init__()

        settings_dict: dict[str, Any] = load_settings(SETTINGS_PATH)
        app_settings.set(settings_dict)

        init_translation(LOCALEDIR)
        set_translation(app_settings.language)
        self.translate_bindings()

        self.board: Board
        self.game: Game

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def on_mount(self) -> None:
        await mount_about_header_icon(
            current_app=self,
            icon=ICON,
            app_metadata=APP_METADATA,
        )
        self.translate_about_header_icon()

        self.create_new_game()

    def translate_bindings(self) -> None:
        for key, binding in KEY_TO_BINDING.items():
            current_binding: Binding = self._bindings.key_to_bindings[key][0]
            self._bindings.key_to_bindings[key] = [
                dataclasses.replace(current_binding, description=_(binding.description))
            ]

    def translate_about_header_icon(self) -> None:
        about_header_icon: AboutHeaderIcon = self.query_one(AboutHeaderIcon)
        about_header_icon.tooltip = _("About")

    def translate(self) -> None:
        self.translate_bindings()
        self.translate_about_header_icon()

    def create_new_game(self):
        if hasattr(self, "game"):
            self.board.remove()

        self.game = Game()

        self.board = Board(self.game)
        self.mount(self.board)

    async def on_click(self, event: Click) -> None:
        if isinstance(event.widget, Widget):
            if event.widget.id == "check":
                await self.on_click_check()

    async def on_click_check(self) -> None:
        code_peg_values: list[int] = []
        for code_peg in self.board.current_row.code_pegs:
            code_peg.query_one("SelectCurrent Static.down-arrow").remove()

            code_peg_value: int
            if isinstance(code_peg.value, int):
                code_peg_value = code_peg.value
            else:
                code_peg_value = 0

            code_peg_values.append(code_peg_value)

        num_red_pegs: int
        num_white_pegs: int
        num_red_pegs, num_white_pegs = await self.game.check_code(
            breaker_code=code_peg_values
        )

        self.board.current_row.query_one("#check").remove()

        self.board.current_row.mount(
            Label(
                "".join(
                    [
                        (FEEDBACK_PEG_COLORS[0] + " ") * num_red_pegs,
                        (FEEDBACK_PEG_COLORS[1] + " ") * num_white_pegs,
                        (BLANK_COLOR + " ")
                        * (self.game.num_pegs - num_red_pegs - num_white_pegs),
                    ]
                ),
                classes="feedback_pegs",
            )
        )

        self.board.current_row.disabled = True

        if num_red_pegs == self.game.num_pegs:
            self.notify(_("Congratulations!"))
        else:
            if self.board.current_row_number < self.game.num_rows:
                self.board.add_row()
            else:
                maker_code: list[int] = self.game.get_maker_code()
                maker_code_str: str = ""
                for color in maker_code:
                    if color == 0:
                        maker_code_str += BLANK_COLOR + " "
                    else:
                        maker_code_str += CODE_PEG_COLORS[color - 1] + " "

                self.notify(
                    f"{_('Better luck next time')}\n{_('Code')}: {maker_code_str}",
                    timeout=30,
                )

    @work
    async def action_new_game(self) -> None:
        if await self.push_screen_wait(
            ConfirmScreen(
                dialog_title="New game",
                dialog_subtitle=APP_METADATA.name,
                question="Are you sure you want to start a new game?",
            )
        ):
            self.create_new_game()

    @work
    async def action_settings(self) -> None:
        setting_rows: dict[str, SettingRow] = {
            key: value
            for key, value in zip(
                app_settings.__dict__.keys(),
                [
                    SettingRow(
                        label="Language:",
                        widget=Select(
                            options=zip(
                                [_(value) for value in LANGUAGES.values()],
                                LANGUAGES.keys(),
                            ),
                            value=app_settings.language,
                            allow_blank=False,
                        ),
                    ),
                    SettingRow(
                        label="Variation:",
                        widget=Select(
                            options=zip(
                                [
                                    variation.description
                                    for variation in VARIATIONS.values()
                                ],
                                VARIATIONS.keys(),
                            ),
                            value=app_settings.variation.name,
                            allow_blank=False,
                        ),
                    ),
                    SettingRow(
                        label="Duplicate colors:",
                        widget=Switch(value=app_settings.duplicate_colors),
                    ),
                    SettingRow(
                        label="Blank color:",
                        widget=Switch(value=app_settings.blank_color),
                    ),
                ],
            )
        }

        settings_dict = await self.push_screen_wait(
            SettingsScreen(
                dialog_title="Settings",
                dialog_subtitle=APP_METADATA.name,
                setting_rows=setting_rows,
            )
        )

        if settings_dict is not None:
            old_language = app_settings.language

            old_variation = app_settings.variation
            old_duplicate_colors = app_settings.duplicate_colors
            old_blank_color = app_settings.blank_color

            app_settings.set(settings_dict)

            if old_language != app_settings.language:
                set_translation(app_settings.language)
                self.translate()

            if (
                old_variation.name != app_settings.variation.name
                or old_duplicate_colors != app_settings.duplicate_colors
                or old_blank_color != app_settings.blank_color
            ):
                self.notify(
                    _("New game settings will be applied to a new game"), timeout=5
                )

            save_settings(settings_dict, SETTINGS_PATH)
