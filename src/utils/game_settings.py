from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from . import constants
from .board import GameType
from .player import TRAIN_CHIP_COLOR


def _enum_by_name(enum_cls, value, default):
    """Accept an enum instance, enum name string, enum value, or fallback."""
    if isinstance(value, enum_cls):
        return value
    if isinstance(value, str):
        try:
            return enum_cls[value]
        except KeyError:
            try:
                return enum_cls(value)
            except ValueError:
                return default
    try:
        return enum_cls(value)
    except (TypeError, ValueError):
        return default


@dataclass
class Settings:
    game_type: GameType
    number_of_players: int
    chip_colors: list[TRAIN_CHIP_COLOR]

    def to_dict(self) -> dict:
        return {
            "game_type": self.game_type.name,
            "number_of_players": self.number_of_players,
            "chip_colors": [color.name for color in self.chip_colors],
        }

    @classmethod
    def from_dict(cls, raw: dict | None) -> "Settings":
        if not isinstance(raw, dict):
            return default_settings()

        game_type = _enum_by_name(GameType, raw.get("game_type"), GameType.LOCAL_GAME)
        try:
            number_of_players = int(raw.get("number_of_players", constants.MIN_PLAYERS))
        except (TypeError, ValueError):
            number_of_players = constants.MIN_PLAYERS
        number_of_players = max(constants.MIN_PLAYERS, min(constants.MAX_PLAYERS, number_of_players))

        raw_colors = raw.get("chip_colors", [])
        colors = normalize_chip_colors(raw_colors, number_of_players)
        return cls(game_type, number_of_players, colors)


def normalize_chip_colors(colors: Iterable | None, number_of_players: int) -> list[TRAIN_CHIP_COLOR]:
    defaults = list(TRAIN_CHIP_COLOR)
    normalized: list[TRAIN_CHIP_COLOR] = []

    if colors is not None:
        for color in colors:
            # Settings UI uses board.TrainChipColors; it has the same names.
            name_or_value = getattr(color, "name", color)
            normalized.append(_enum_by_name(TRAIN_CHIP_COLOR, name_or_value, TRAIN_CHIP_COLOR.RED))

    for default_color in defaults:
        if len(normalized) >= number_of_players:
            break
        if default_color not in normalized:
            normalized.append(default_color)

    while len(normalized) < number_of_players:
        normalized.append(defaults[len(normalized) % len(defaults)])

    return normalized[:number_of_players]


def default_settings() -> Settings:
    return Settings(
        game_type=GameType.LOCAL_GAME,
        number_of_players=constants.MIN_PLAYERS,
        chip_colors=[TRAIN_CHIP_COLOR.RED, TRAIN_CHIP_COLOR.BLACK],
    )


class GameSettings:
    """Serializable settings wrapper shared by menu, settings screen, and game scene."""

    def __init__(self, settings: Settings | None = None):
        self.__settings = settings or default_settings()

    @property
    def get_settings(self) -> Settings:
        return self.__settings

    @property
    def game_type(self) -> GameType:
        return self.__settings.game_type

    @property
    def number_of_players(self) -> int:
        return self.__settings.number_of_players

    @property
    def chip_colors(self) -> list[TRAIN_CHIP_COLOR]:
        return list(self.__settings.chip_colors)

    def update_settings(self, gt: GameType, np: int, cc: list) -> None:
        np = max(constants.MIN_PLAYERS, min(constants.MAX_PLAYERS, int(np)))
        game_type = _enum_by_name(GameType, getattr(gt, "name", gt), GameType.LOCAL_GAME)
        chip_colors = normalize_chip_colors(cc, np)
        self.__settings = Settings(game_type, np, chip_colors)

    def to_dict(self) -> dict:
        return self.__settings.to_dict()

    def save(self, path: str | Path | None = None) -> None:
        destination = Path(path) if path else constants.SETTINGS_FILE
        destination.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path | None = None) -> "GameSettings":
        source = Path(path) if path else constants.SETTINGS_FILE
        if not source.exists():
            return cls()
        try:
            raw = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        return cls(Settings.from_dict(raw))
