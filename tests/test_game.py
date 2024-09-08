import pytest
import polars as pl
import numpy as np
from unittest.mock import patch, MagicMock
from pybaseball_live.game import (
    games,
    _game_to_df,
    _extract_play_data,
    _extract_event_data,
    _extract_walk_data,
    _get_team_data,
    _get_count_data,
    _get_pitch_data,
    _get_hit_data,
    _get_ab_result,
)


@pytest.fixture
def sample_game_data():
    return {
        "gamePk": 12345,
        "gameData": {
            "datetime": {"officialDate": "2023-07-01"},
            "teams": {
                "away": {"abbreviation": "NYY", "id": 1},
                "home": {"abbreviation": "BOS", "id": 2},
            },
        },
        "liveData": {
            "plays": {
                "allPlays": [
                    {
                        "result": {
                            "type": "atBat",
                            "event": "Single",
                            "eventType": "single",
                        },
                        "about": {"isTopInning": True},
                        "matchup": {
                            "batter": {"id": 123, "fullName": "John Doe"},
                            "pitcher": {"id": 456, "fullName": "Jane Smith"},
                            "batSide": {"code": "R"},
                            "pitchHand": {"code": "L"},
                        },
                        "playEvents": [
                            {
                                "details": {
                                    "call": {"code": "B"},
                                    "description": "Ball",
                                },
                                "count": {"balls": 1, "strikes": 0, "outs": 0},
                                "pitchData": {"startSpeed": 90.5},
                                "index": 0,
                                "playId": "play1",
                                "isPitch": True,
                            },
                            {
                                "details": {
                                    "call": {"code": "S"},
                                    "description": "Strike",
                                },
                                "count": {"balls": 1, "strikes": 1, "outs": 0},
                                "pitchData": {"startSpeed": 92.0},
                                "index": 1,
                                "playId": "play2",
                                "isPitch": True,
                            },
                        ],
                    }
                ]
            }
        },
    }


def test_games():
    with patch("pybaseball_live.game.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"gamePk": 12345}
        mock_get.return_value = mock_response

        result = games([12345])
        assert isinstance(result, dict)
        assert 12345 in result
        assert isinstance(result[12345], pl.DataFrame)


def test_game_to_df(sample_game_data):
    df = _game_to_df(sample_game_data)
    assert isinstance(df, pl.DataFrame)
    assert "game_id" in df.columns
    assert "game_date" in df.columns
    assert df.shape[0] > 0


def test_extract_play_data(sample_game_data):
    play = sample_game_data["liveData"]["plays"]["allPlays"][0]
    result = _extract_play_data(play, sample_game_data)
    assert isinstance(result, list)
    assert len(result) == 2  # Two pitch events in the sample data


def test_extract_event_data(sample_game_data):
    play = sample_game_data["liveData"]["plays"]["allPlays"][0]
    event = play["playEvents"][0]
    result = _extract_event_data(play, event, 0, play["playEvents"])
    assert isinstance(result, dict)
    assert "batter_id" in result
    assert "pitcher_id" in result


def test_extract_walk_data(sample_game_data):
    play = sample_game_data["liveData"]["plays"]["allPlays"][0]
    event = play["playEvents"][0]
    event["count"]["balls"] = 4  # Simulate a walk
    result = _extract_walk_data(play, event, sample_game_data)
    assert isinstance(result, dict)
    assert "batter_id" in result
    assert "pitcher_id" in result


def test_get_team_data(sample_game_data):
    play = sample_game_data["liveData"]["plays"]["allPlays"][0]
    about = {"isTopInning": True}
    result = _get_team_data(about, play)
    assert isinstance(result, dict)
    assert "batter_team" in result
    assert "pitcher_team" in result


def test_get_count_data(sample_game_data):
    play = sample_game_data["liveData"]["plays"]["allPlays"][0]
    event = play["playEvents"][0]
    result = _get_count_data(play, event, 0)
    assert isinstance(result, dict)
    assert "strikes" in result
    assert "balls" in result
    assert "outs" in result


def test_get_pitch_data():
    pitch_data = {
        "startSpeed": 90.5,
        "endSpeed": 83.2,
        "strikeZoneTop": 3.5,
        "strikeZoneBottom": 1.5,
        "coordinates": {"x": 0.5, "y": 2.0},
        "breaks": {"spinRate": 2500},
    }
    result = _get_pitch_data(pitch_data)
    assert isinstance(result, dict)
    assert "start_speed" in result
    assert "end_speed" in result
    assert "spin_rate" in result


def test_get_hit_data():
    hit_data = {
        "launchSpeed": 95.0,
        "launchAngle": 25.0,
        "totalDistance": 350,
        "location": "7",
        "coordinates": {"coordX": 125.5, "coordY": 200.3},
    }
    result = _get_hit_data(hit_data)
    assert isinstance(result, dict)
    assert "launch_speed" in result
    assert "launch_angle" in result
    assert "hit_x" in result
    assert "hit_y" in result


def test_get_ab_result(sample_game_data):
    play = sample_game_data["liveData"]["plays"]["allPlays"][0]
    result_last = _get_ab_result(play, 1, 1)  # Last event
    result_not_last = _get_ab_result(play, 0, 1)  # Not last event
    assert isinstance(result_last, dict)
    assert isinstance(result_not_last, dict)
    assert result_last["type_ab"] is not None
