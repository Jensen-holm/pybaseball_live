import sys
import os

sys.path.append(os.path.abspath(".."))

from pybaseball_live.sport_id import sports, check_sport_id


def test_sports_df() -> None:
    _ = sports()


def test_check_sport_id() -> None:
    id_df = sports()
    assert all(
        [True if check_sport_id(_id) is not None else False for _id in id_df["id"]]
    )
