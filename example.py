from pybaseball_live.schedule import schedule_range
from pybaseball_live.game import games
import datetime
import time

if __name__ == "__main__":
    todays_schedule = schedule_range(
        sport_ids=[1],
        game_types=["R"],
        start_dt=datetime.datetime.now().date(),
        end_dt=datetime.datetime.now().date(),
    )

    assert todays_schedule is not None
    assert "game_id" in todays_schedule.columns

    todays_game_ids = todays_schedule["game_id"].to_list()
    while True:
        game_data = games(todays_game_ids)
        for game_df in game_data.values():
            print(game_df)

        time.sleep(1)
