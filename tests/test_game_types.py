import sys
import os

sys.path.append(os.path.abspath(".."))

from live_pybaseball.game_types import game_types


def test_game_types() -> None:
    _ = game_types()
