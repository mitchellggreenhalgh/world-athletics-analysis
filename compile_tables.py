from world_athletics_scraper import WorldAthleticsScraper

scraper = WorldAthleticsScraper()

try: 
    scraper.compile_all_time_tables()
except Exception as e:
    print(repr(e))

try:
    scraper.compile_season_bests_tables()
except Exception as e:
    print(repr(e))

