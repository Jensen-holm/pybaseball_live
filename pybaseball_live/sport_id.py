from typing import Optional
import polars as pl
import requests

from .utils import ENDPOINT_URL
from .exceptions import BadResponseCode, BadResponseData

__all__ = ["sports", "check_sport_id"]

SPORT_URL = ENDPOINT_URL.format(endpoint="sports")


def sports() -> pl.DataFrame:
    """
    Retrieves the list of sports from the MLB API and processes it into a Polars DataFrame.

    Raises
    - live_pybaseball.exceptions.BadResponseCode: if response.status_code != 200
    - live_pybaseball.exceptions.BadResponseData: if response.json() does not have the key 'sports'

    Returns:
    - pl.DataFrame: A DataFrame containing the sports information.
    """
    response = requests.get(SPORT_URL)
    if response.status_code != 200:
        raise BadResponseCode(url=SPORT_URL, bad_code=response.status_code)

    json = response.json()
    if (sports_data := json.get("sports", None)) is None:
        raise BadResponseData(url=SPORT_URL, key="sports")
    return pl.DataFrame(sports_data)


def check_sport_id(sport_id: int) -> Optional[pl.DataFrame]:
    """
    Checks if the provided sport ID exists in the list of sports retrieved from the MLB API.

    Parameters:
    - sport_id (int): The sport ID to check.

    Raises:
    - live_pybaseball.exceptions.BadResponseData: if 'id' is not a key in sports() df

    Returns:
    - Optional[pl.DataFrame]: returns the dataframe if the sport exists, None if it is not
    """
    sport_id_df = sports()

    if sport_id not in sport_id_df["id"]:
        return None
    return sport_id_df.filter(pl.col("id") == sport_id)
