from pybaseball_live.schedule import schedule


if __name__ == "__main__":
    schedule_df_2024_2023 = schedule(years=[2024, 2023])
    print(schedule_df_2024_2023)
