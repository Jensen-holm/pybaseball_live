import sys
import os

sys.path.append(os.path.abspath(".."))

from live_pybaseball.schedule import schedule


def test_schedule() -> None:
    _ = schedule()
