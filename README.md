# MLB Scraper

This Python module provides a class `MLB_Scrape` that interacts with the MLB Stats API to retrieve various types of baseball-related data. The data is processed and returned as Polars DataFrames for easy manipulation and analysis.

## Install Dependencies

`pip install -r requirements.txt`

## Useage

Getting the full regular season schedules for years 2023 & 2024 

Code:
```python
from pybaseball_live.schedule import schedule

if __name__ == "__main__":
    schedule_df_2024_2023 = schedule(years=[2024, 2023], game_types=["R"])
    print(schedule_df_2024_2023)
```

Output:
┌─────────┬──────────┬────────────┬──────────────────────┬──────────────────────┬───────┬──────────┬───────────────────────┐
│ game_id ┆ time     ┆ date       ┆ away                 ┆ home                 ┆ state ┆ venue_id ┆ venue_name            │
│ ---     ┆ ---      ┆ ---        ┆ ---                  ┆ ---                  ┆ ---   ┆ ---      ┆ ---                   │
│ i64     ┆ str      ┆ date       ┆ str                  ┆ str                  ┆ str   ┆ i64      ┆ str                   │
╞═════════╪══════════╪════════════╪══════════════════════╪══════════════════════╪═══════╪══════════╪═══════════════════════╡
│ 718768  ┆ 07:08 PM ┆ 2023-03-30 ┆ Chicago White Sox    ┆ Houston Astros       ┆ F     ┆ 2392     ┆ Minute Maid Park      │
│ 718780  ┆ 01:05 PM ┆ 2023-03-30 ┆ Atlanta Braves       ┆ Washington Nationals ┆ F     ┆ 3309     ┆ Nationals Park        │
│ 718777  ┆ 02:20 PM ┆ 2023-03-30 ┆ Milwaukee Brewers    ┆ Chicago Cubs         ┆ F     ┆ 17       ┆ Wrigley Field         │
│ 718774  ┆ 04:10 PM ┆ 2023-03-30 ┆ New York Mets        ┆ Miami Marlins        ┆ F     ┆ 4169     ┆ loanDepot park        │
│ 718781  ┆ 01:05 PM ┆ 2023-03-30 ┆ San Francisco Giants ┆ New York Yankees     ┆ F     ┆ 3313     ┆ Yankee Stadium        │
│ …       ┆ …        ┆ …          ┆ …                    ┆ …                    ┆ …     ┆ …        ┆ …                     │
│ 746577  ┆ 03:10 PM ┆ 2024-09-29 ┆ Houston Astros       ┆ Cleveland Guardians  ┆ S     ┆ 5        ┆ Progressive Field     │
│ 744880  ┆ 03:07 PM ┆ 2024-09-29 ┆ Miami Marlins        ┆ Toronto Blue Jays    ┆ S     ┆ 14       ┆ Rogers Centre         │
│ 745282  ┆ 03:05 PM ┆ 2024-09-29 ┆ St. Louis Cardinals  ┆ San Francisco Giants ┆ S     ┆ 2395     ┆ Oracle Park           │
│ 745932  ┆ 03:10 PM ┆ 2024-09-29 ┆ New York Mets        ┆ Milwaukee Brewers    ┆ S     ┆ 32       ┆ American Family Field │
│ 747147  ┆ 03:10 PM ┆ 2024-09-29 ┆ San Diego Padres     ┆ Arizona Diamondbacks ┆ S     ┆ 15       ┆ Chase Field           │
└─────────┴──────────┴────────────┴──────────────────────┴──────────────────────┴───────┴──────────┴───────────────────────┘

## Contributing 

Pull requests and issues are welcome, when making changes...

1. fork this repository
2. make new branch
3. make changes
4. run tests
5. open pull request

if your changes add new functionality, make sure to add tests for it in the ./tests directory.

To run tests, make sure you're in the main directory of the repository, then run

`pytest ./tests`
