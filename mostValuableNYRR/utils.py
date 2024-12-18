import pandas as pd
import datetime

def sum_results(gender):
    athlete_values = dict()
    for x in range(2016, 2025):
        if x == 2020:
            continue
        results_df = pd.read_csv(f"{gender}_{x}.csv")
        for i, row in results_df.iterrows():
            key = f"{row['firstName']} {row['lastName']}"
            if athlete_values.get(key):
                athlete_values[key]["TotalPoints"]+= row["points_scored"]
                athlete_values[key]["NumRaces"] += 1
            else:
                athlete_values[key]= {"Name": key, "TotalPoints":row["points_scored"], "NumRaces": 1}
    athlete_values = [athlete_values[key] for key in athlete_values.keys()]
    athlete_values = pd.DataFrame(athlete_values)
    return athlete_values.sort_values("TotalPoints", ascending=False)

def full_result_db(gender):
    full_results = []
    for x in range(2016, 2025):
        if x == 2020:
            continue
        results_df = pd.read_csv(f"{gender}_{x}.csv")
        for i, row in results_df.iterrows():
            if pd.isnull(row["finishTime"]):
                finish_time = row["overallTime"]
            else:
                finish_time = str(datetime.timedelta(seconds=int(row["finishTime"])//1000))
            if pd.isnull(row["finishPlace"]):
                finish_place = row["genderPlace"]
            else:
                finish_place = row["finishPlace"]
            new_values = {
                "Name": f'{row["firstName"]} {row["lastName"]}',
                "Gender": row["gender"],
                "Age": row["age"],
                "Year": x,
                "EventCode": row["event_code"],
                "PointsScored": row["points_scored"],
                "TeamCode": row["team_code"],
                "TeamPlace": row["team_place"],
                "PlaceOnteam": row["place_on_team"],
                "FinishTime": finish_time,
                "FinishPlace": finish_place
            }
            full_results.append(new_values)
    return pd.DataFrame(full_results)

def get_line_graph_results(df):
    unique_names = df.Name.unique()
    results=dict()
    for x in unique_names:
        runner_df = df[df["Name"] == x]
        running_total_points = []
        points = 0
        for y in range(2015, 2025):
            runner_year_df = runner_df[runner_df["Year"] == y]
            for i, row in runner_year_df.iterrows():
                points += row["PointsScored"]
            running_total_points.append(points)
        results[x] = running_total_points
    
    line_graph_df = pd.DataFrame(results, index=[x for x in range(2015,2025)])
    return line_graph_df

def get_line_graph_for_athlete(df, names):
    results=dict()
    for x in names:
        runner_df = df[df["Name"] == x]
        running_total_points = []
        points = 0
        for y in range(2015, 2025):
            runner_year_df = runner_df[runner_df["Year"] == y]
            for i, row in runner_year_df.iterrows():
                points += row["PointsScored"]
            running_total_points.append(points)
        results[x] = running_total_points
    
    line_graph_df = pd.DataFrame(results, index=[x for x in range(2015,2025)])
    return line_graph_df

def sum_results_by_year(gender):
    athlete_values = dict()
    for x in range(2016, 2025):
        if x == 2020:
            continue
        results_df = pd.read_csv(f"{gender}_{x}.csv")
        for i, row in results_df.iterrows():
            key = f"{row['firstName']} {row['lastName']} {x}"
            if athlete_values.get(key):
                athlete_values[key]["TotalPoints"]+= row["points_scored"]
                athlete_values[key]["NumRaces"] += 1
            else:
                athlete_values[key]= {"Name": key, "TotalPoints":row["points_scored"], "NumRaces": 1}
    athlete_values = [athlete_values[key] for key in athlete_values.keys()]
    athlete_values = pd.DataFrame(athlete_values)
    return athlete_values.sort_values("TotalPoints", ascending=False)