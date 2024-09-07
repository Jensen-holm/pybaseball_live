import polars as pl
import requests

from .utils import ENDPOINT_URL
from .exceptions import BadResponseCode

__all__ = ["game_types"]


GAME_TYPES_URL = ENDPOINT_URL.format(endpoint="gameTypes")


def game_types() -> pl.DataFrame:
    """
    Retrieves the different types of MLB games from the MLB API and processes them into a Polars DataFrame.

    Raises:
    - live_pybaseball.exceptions.BadResponseCode: if response.status_code != 200

    Returns:
    - df (pl.DataFrame): A DataFrame containing the game types information.
    """
    response = requests.get(GAME_TYPES_URL)
    if response.status_code != 200:
        raise BadResponseCode(url=GAME_TYPES_URL, bad_code=response.status_code)

    json = response.json()
    return pl.DataFrame(json)
