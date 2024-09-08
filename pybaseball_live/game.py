from typing import Tuple
import polars as pl
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import GAME_ENDPOINT_ROOT
from .exceptions import BadResponseCode


__all__ = ["games"]


def games(game_ids: list[int]) -> dict[int, pl.DataFrame]:
    """
    Retrieves live game data for a collection of live game ID's in parallel

    @params:
        - games: collection of game IDs for which to retrieve live data

    @returns:
        - dict[int, pl.DataFrame]: dictionary of game_id to game dataframe
    """

    def _game(game_id: int) -> Tuple[int, pl.DataFrame]:
        live_game_url = GAME_ENDPOINT_ROOT.format(game_id=game_id)
        if (response := requests.get(live_game_url)).status_code != 200:
            raise BadResponseCode(url=live_game_url, bad_code=response.status_code)
        return game_id, _game_to_df(response.json())

    game_data: dict[int, pl.DataFrame] = {}
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(_game, game_id) for game_id in game_ids]
        for future in as_completed(futures):
            try:
                game_id, df = future.result()
                game_data[game_id] = df
            except Exception as e:
                print(f"An error occurred while processing game: {e}")
    return game_data


def _game_to_df(game_data: dict) -> pl.DataFrame:
    """
    Converts a dictionary of game_data into polars data frame format.

    @params:
        - game_data: game information in dictionary format

    @returns:
        - pl.DataFrame: dataframe containing data from all of the plays in game_data
    """
    game_id = game_data.get("gamePk")
    game_date = game_data.get("gameData", {}).get("datetime", {}).get("officialDate")
    all_plays = game_data.get("liveData", {}).get("plays", {}).get("allPlays", [])

    flattened_data = [
        {**event_data, "game_id": game_id, "game_date": game_date}
        for play in all_plays
        for event_data in _extract_play_data(play, game_data)
    ]

    return pl.DataFrame(flattened_data)


def _extract_play_data(play: dict, game_data: dict) -> list[dict]:
    """
    Extracts data from a single play.

    @params:
        - play: dictionary containing play data
        - game_data: full game data dictionary

    @returns:
        - list[dict]: list of extracted event data dictionaries
    """
    play_events = play.get("playEvents", [])
    ab_data = []

    for n, event in enumerate(play_events):
        if event.get("isPitch") or "call" in event.get("details", {}):
            event_data = _extract_event_data(play, event, n, play_events)
        elif event.get("count", {}).get("balls") == 4:
            event_data = _extract_walk_data(play, event, game_data)
        else:
            continue
        ab_data.append(event_data)

    return ab_data


def _extract_event_data(play: dict, event: dict, n: int, play_events: list) -> dict:
    """
    Extracts data from a single event in a play.

    @params:
        - play: dictionary containing play data
        - event: dictionary containing event data
        - n: index of the event in the play
        - play_events: list of all events in the play

    @returns:
        - dict: extracted event data
    """
    matchup = play.get("matchup", {})
    about = play.get("about", {})
    details = event.get("details", {})

    swing_list = ["X", "F", "S", "D", "E", "T", "W"]
    whiff_list = ["S", "T", "W"]

    return {
        "batter_id": matchup.get("batter", {}).get("id"),
        "batter_name": matchup.get("batter", {}).get("fullName"),
        "batter_hand": matchup.get("batSide", {}).get("code"),
        "pitcher_id": matchup.get("pitcher", {}).get("id"),
        "pitcher_name": matchup.get("pitcher", {}).get("fullName"),
        "pitcher_hand": matchup.get("pitchHand", {}).get("code"),
        **_get_team_data(about, play),
        **_get_count_data(play, event, n),
        "play_description": details.get("description"),
        "play_code": details.get("code"),
        "in_play": details.get("isInPlay"),
        "is_strike": details.get("isStrike"),
        "is_swing": (
            details.get("code") in swing_list if details.get("code") else np.nan
        ),
        "is_whiff": (
            details.get("code") in whiff_list if details.get("code") else np.nan
        ),
        "is_ball": details.get("isBall"),
        "is_review": details.get("hasReview"),
        "pitch_type": details.get("type", {}).get("code"),
        "pitch_description": details.get("type", {}).get("description"),
        **_get_pitch_data(event.get("pitchData", {})),
        **_get_hit_data(event.get("hitData", {})),
        "index_play": event.get("index"),
        "play_id": event.get("playId"),
        "start_time": event.get("startTime"),
        "end_time": event.get("endTime"),
        "is_pitch": event.get("isPitch"),
        "type_type": event.get("type"),
        **_get_ab_result(play, n, len(play_events) - 1),
    }


def _extract_walk_data(play: dict, event: dict, game_data: dict) -> dict:
    """
    Extracts data for a walk event.

    @params:
        - play: dictionary containing play data
        - event: dictionary containing event data
        - game_data: full game data dictionary

    @returns:
        - dict: extracted walk event data
    """
    matchup = play.get("matchup", {})
    about = play.get("about", {})
    count = event.get("count", {})

    base_data = {
        "batter_id": matchup.get("batter", {}).get("id"),
        "batter_name": matchup.get("batter", {}).get("fullName"),
        "batter_hand": matchup.get("batSide", {}).get("code"),
        "pitcher_id": matchup.get("pitcher", {}).get("id"),
        "pitcher_name": matchup.get("pitcher", {}).get("fullName"),
        "pitcher_hand": matchup.get("pitchHand", {}).get("code"),
        **_get_team_data(about, play),
        **{k: count.get(k) for k in ["strikes", "balls", "outs"]},
        **{f"{k}_after": count.get(k) for k in ["strikes", "balls", "outs"]},
        "index_play": event.get("index"),
        "play_id": event.get("playId"),
        "start_time": event.get("startTime"),
        "end_time": event.get("endTime"),
        "is_pitch": event.get("isPitch"),
        "type_type": event.get("type"),
        "event": play.get("result", {}).get("event"),
        "event_type": play.get("result", {}).get("eventType"),
    }

    # Fill remaining fields with np.nan
    remaining_fields = [
        "play_description",
        "play_code",
        "in_play",
        "is_strike",
        "is_swing",
        "is_whiff",
        "is_ball",
        "is_review",
        "pitch_type",
        "pitch_description",
        "ab_number",
        "start_speed",
        "end_speed",
        "sz_top",
        "sz_bot",
        "x",
        "y",
        "ax",
        "ay",
        "az",
        "pfxx",
        "pfxz",
        "px",
        "pz",
        "vx0",
        "vy0",
        "vz0",
        "x0",
        "y0",
        "z0",
        "zone",
        "type_confidence",
        "plate_time",
        "extension",
        "spin_rate",
        "spin_direction",
        "vb",
        "ivb",
        "hb",
        "launch_speed",
        "launch_angle",
        "launch_distance",
        "launch_location",
        "trajectory",
        "hardness",
        "hit_x",
        "hit_y",
        "type_ab",
        "rbi",
        "away_score",
        "home_score",
        "is_out",
    ]
    base_data.update({field: np.nan for field in remaining_fields})

    return base_data


def _get_team_data(about: dict, play: dict) -> dict:
    """
    Extracts team data for batter and pitcher.

    @params:
        - about: dictionary containing game state information
        - play: dictionary containing play data

    @returns:
        - dict: team data for batter and pitcher
    """
    game_data = play.get("game", {}).get("gameData", {})
    is_top_inning = about.get("isTopInning")

    batter_team = "away" if is_top_inning else "home"
    pitcher_team = "home" if is_top_inning else "away"

    return {
        "batter_team": game_data.get("teams", {})
        .get(batter_team, {})
        .get("abbreviation"),
        "batter_team_id": game_data.get("teams", {}).get(batter_team, {}).get("id"),
        "pitcher_team": game_data.get("teams", {})
        .get(pitcher_team, {})
        .get("abbreviation"),
        "pitcher_team_id": game_data.get("teams", {}).get(pitcher_team, {}).get("id"),
    }


def _get_count_data(play: dict, event: dict, n: int) -> dict:
    """
    Extracts count data for an event.

    @params:
        - play: dictionary containing play data
        - event: dictionary containing event data
        - n: index of the event in the play

    @returns:
        - dict: count data before and after the event
    """
    play_events = play.get("playEvents", [])
    count = event.get("count", {})

    if n == 0:
        prev_count = {"strikes": 0, "balls": 0, "outs": count.get("outs")}
    else:
        prev_count = play_events[n - 1].get("count", {})

    return {
        "strikes": prev_count.get("strikes"),
        "balls": prev_count.get("balls"),
        "outs": prev_count.get("outs"),
        "strikes_after": count.get("strikes"),
        "balls_after": count.get("balls"),
        "outs_after": count.get("outs"),
    }


def _get_pitch_data(pitch_data: dict) -> dict:
    """
    Extracts pitch data from the pitch_data dictionary.

    @params:
        - pitch_data: dictionary containing pitch data

    @returns:
        - dict: extracted pitch data
    """
    coordinates = pitch_data.get("coordinates", {})
    breaks = pitch_data.get("breaks", {})

    return {
        "start_speed": pitch_data.get("startSpeed"),
        "end_speed": pitch_data.get("endSpeed"),
        "sz_top": pitch_data.get("strikeZoneTop"),
        "sz_bot": pitch_data.get("strikeZoneBottom"),
        "x": coordinates.get("x"),
        "y": coordinates.get("y"),
        "ax": coordinates.get("aX"),
        "ay": coordinates.get("aY"),
        "az": coordinates.get("aZ"),
        "pfxx": coordinates.get("pfxX"),
        "pfxz": coordinates.get("pfxZ"),
        "px": coordinates.get("pX"),
        "pz": coordinates.get("pZ"),
        "vx0": coordinates.get("vX0"),
        "vy0": coordinates.get("vY0"),
        "vz0": coordinates.get("vZ0"),
        "x0": coordinates.get("x0"),
        "y0": coordinates.get("y0"),
        "z0": coordinates.get("z0"),
        "zone": pitch_data.get("zone"),
        "type_confidence": pitch_data.get("typeConfidence"),
        "plate_time": pitch_data.get("plateTime"),
        "extension": pitch_data.get("extension"),
        "spin_rate": breaks.get("spinRate"),
        "spin_direction": breaks.get("spinDirection"),
        "vb": breaks.get("breakVertical"),
        "ivb": breaks.get("breakVerticalInduced"),
        "hb": breaks.get("breakHorizontal"),
    }


def _get_hit_data(hit_data: dict) -> dict:
    """
    Extracts hit data from the hit_data dictionary.

    @params:
        - hit_data: dictionary containing hit data

    @returns:
        - dict: extracted hit data
    """
    coordinates = hit_data.get("coordinates", {})

    return {
        "launch_speed": hit_data.get("launchSpeed"),
        "launch_angle": hit_data.get("launchAngle"),
        "launch_distance": hit_data.get("totalDistance"),
        "launch_location": hit_data.get("location"),
        "trajectory": hit_data.get("trajectory"),
        "hardness": hit_data.get("hardness"),
        "hit_x": coordinates.get("coordX"),
        "hit_y": coordinates.get("coordY"),
    }


def _get_ab_result(play: dict, n: int, last_event_index: int) -> dict:
    """
    Extracts at-bat result data.

    @params:
        - play: dictionary containing play data
        - n: index of the current event
        - last_event_index: index of the last event in the play

    @returns:
        - dict: at-bat result data
    """
    result = play.get("result", {})

    if n == last_event_index:
        return {
            "type_ab": result.get("type"),
            "event": result.get("event"),
            "event_type": result.get("eventType"),
            "rbi": result.get("rbi"),
            "away_score": result.get("awayScore"),
            "home_score": result.get("homeScore"),
            "is_out": result.get("isOut"),
        }
    return {
        "type_ab": np.nan,
        "event": np.nan,
        "event_type": np.nan,
        "rbi": np.nan,
        "away_score": np.nan,
        "home_score": np.nan,
        "is_out": np.nan,
    }
