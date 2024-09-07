import sys
import os

sys.path.append(os.path.abspath(".."))

from pybaseball_live.schedule import schedule


def test_schedule() -> None:
    _ = schedule()
