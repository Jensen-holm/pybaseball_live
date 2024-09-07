from typing import Optional
import polars as pl
import datetime
import requests

from .utils import ENDPOINT_URL
from .exceptions import BadResponseCode

__all__ = ["schedule"]


SCHEDULE_URL = ENDPOINT_URL.format(endpoint="schedule")

SCHEDULE_FILTER = (
    SCHEDULE_URL
    + "?sportId={sport_ids}&gameTypes={game_types}&season={years}&hydrate=lineup,players"
)


def schedule(
    years: list[int] = [datetime.datetime.now().year],
    sport_ids: list[int] = [1],
    game_types: list[int] = ["R"],
) -> Optional[pl.DataFrame]:
    """
    Retrieves the schedule of baseball games based on the specified parameters.

    Parameters:
    - years (list): A list of years to filter the schedule. Default is [current_year].
    - sport_ids (list): A list of sport IDs to filter the schedule. Default is [1].
    - game_types (list): A list of game types to filter the schedule. Default is ['R'].

    Returns:
    - game_df Optional(polars.DataFrame): A DataFrame containing the game schedule information,
        including game ID, date, time, away team, home team, game state, venue ID, and venue name.
        Returns None if the resulting data is empty.
    """
    assert isinstance(years, list), f"'years' must be a list in 'schedule()'"
    assert isinstance(sport_ids, list), f"'sport_ids' must be a list in 'schedule()'"
    assert isinstance(game_types, list), f"'game_types' must be a list in 'schedule()'"

    # convert the years, sport_ids, and game_types into a csv string for the SCHEDULE_URL
    schedule_filter_args = {
        arg_name: ",".join([str(v) for v in values])
        for arg_name, values in {
            "years": years,
            "sport_ids": sport_ids,
            "game_types": game_types,
        }.items()
    }

    url = SCHEDULE_FILTER.format(**schedule_filter_args)
    if (response := requests.get(url)).status_code != 200:
        raise BadResponseCode(url=url, bad_code=response.status_code)

    json = response.json()

    # Flatten the nested structure
    flattened_data = []
    for date_entry in json.get("dates", []):
        for game in date_entry.get("games", []):
            game_data = {
                "game_id": game.get("gamePk"),
                "time": game.get("gameDate"),
                "date": game.get("officialDate"),
                "away": game.get("teams", {})
                .get("away", {})
                .get("team", {})
                .get("name"),
                "home": game.get("teams", {})
                .get("home", {})
                .get("team", {})
                .get("name"),
                "state": game.get("status", {}).get("codedGameState"),
                "venue_id": game.get("venue", {}).get("id"),
                "venue_name": game.get("venue", {}).get("name"),
            }
            flattened_data.append(game_data)

    # create new df using flattened data, if it is empty return None
    if (game_df := pl.DataFrame(flattened_data)).is_empty():
        return None
    return (
        game_df.with_columns(
            pl.col("date").str.to_date(),
            pl.col("time")
            .str.to_datetime()
            .dt.replace_time_zone("UTC")
            .dt.convert_time_zone("US/Eastern")
            .dt.strftime("%I:%M %p"),
        )
        .unique(subset="game_id")
        .sort("date")
    )
