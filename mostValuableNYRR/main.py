import nyrr_client
client = nyrr_client.NYRRClient()

for x in range(2024, 2025):
    men_2024 = client.get_season_results(f"{x}", "AM")

    men_2024.to_csv(f"men_{x}.csv")

    women_2024 = client.get_season_results(f"{x}", "AW")
    women_2024.to_csv(f"women_{x}.csv")

