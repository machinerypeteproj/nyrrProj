import requests, json
import pandas as pd
import time

POINTS_TABLE= {
    "1": 15,
    "2": 12,
    "3": 10,
    "4": 8,
    "5": 6,
    "6": 5,
    "7": 4,
    "8": 3,
    "9": 2
}

NORM_POINTS_DIST = {
    "1": (5/15),
    "2": (4/15),
    "3": (3/15),
    "4": (2/15),
    "5": (1/15)
}

TC_POINTS_DIST = {
    "1": (10/55),
    "2": (9/55),
    "3": (8/55),
    "4": (7/55),
    "5": (6/55),
    "6": (5/55),
    "7": (4/55),
    "8": (3/55),
    "9": (2/55),
    "10": (1/55)
}

MARATHON_POINTS_DIST = {
    "1": (8/15),
    "2": (5/15),
    "3": (2/15)
}

GENDER_TABLE = {
    "AW": "W",
    "AM": "M",
    "AX": "X"
}



HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json;charset=UTF-8",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
}

SCOT16_M_TABLE = {
    "WSX": 1,
    "NYAC": 2,
    "CPTC": 3,
    "NBR": 4,
    "DWRT": 5,
    "UATH": 6,
    "QDR": 7,
    "FRNY": 8,
    "NYH": 9
}

SCOT16_W_TABLE = {
    "NYAC": 2,
    "CPTC": 1,
    "DWRT": 3,
    "HHRT": 4,
    "NYH": 7,
    "GCTR": 6,
    "VCTC": 8,
    "FRNY": 9
}

class NYRRClient():
    def __init__(self) -> None:
        pass

    def get_season_results(self, year, divisionCode):
        r = requests.post("https://rmsprodapi.nyrr.org/api/v2/ClubStandings/getDivisionResults", headers=HEADERS, json={"divisionCode": divisionCode, "year": year})
        retries = 1
        while r.status_code != 200:
            print(f"Request to NYRR Failed with Code {r.status_code}, Retrying in {5*retries}")
            time.sleep(5*retries)
            retries+=1
            r = requests.post("https://rmsprodapi.nyrr.org/api/v2/ClubStandings/getDivisionResults", headers=HEADERS, json={"divisionCode": divisionCode, "year": year})
        
    
        races = json.loads(r.content)['items'][0]["eventDetails"]
        full_season_results = []
        for race in races:
            if race["eventCode"] == "SCOT16":
                full_season_results.extend(self.scotland_2016(GENDER_TABLE[divisionCode]))
            else:
                team_champs = ("Team Championship" in race["eventName"])
                marathon = ("Marathon" in race["eventName"])
                if "draft" not in race["eventCode"]:
                    full_season_results.extend(self.get_team_results(race["eventCode"], GENDER_TABLE[divisionCode], team_champs, marathon))
        
        df = pd.DataFrame(full_season_results)
        return df
    
    def get_team_results(self, event_code, gender, team_champs=False, marathon=False):
        r = requests.post("https://rmsprodapi.nyrr.org/api/v2/awards/teamAwards", headers=HEADERS, json={"eventCode": event_code, "teamCode": None})
        retries = 1
        while r.status_code != 200:
            print(f"Request to NYRR Failed with Code {r.status_code}, Retrying in {5*retries}")
            time.sleep(5*retries)
            retries+=1
            r = requests.post("https://rmsprodapi.nyrr.org/api/v2/awards/teamAwards", headers=HEADERS, json={"eventCode": event_code, "teamCode": None})

        all_teams =  json.loads(r.content)['items']
        
        df = pd.DataFrame(all_teams)

        df = df[df["minimumAge"] == 0]
        
        df = df[df["teamGender"] == gender]
        if team_champs:
            df = df[df["runnersCount"] == 10]
            points_dist_table = TC_POINTS_DIST
        elif marathon:
            df = df[df["runnersCount"] == 3]
            points_dist_table = MARATHON_POINTS_DIST
        else:
            df = df[df["runnersCount"] == 5]
            points_dist_table = NORM_POINTS_DIST

        all_runner_results = []
        for i, row in df.iterrows():
            all_runner_results.extend(self._get_single_team_results(event_code, row["teamCode"], row["teamGender"], row["teamOrder"], points_dist_table, team_champs))

        return all_runner_results

    
    def _get_single_team_results(self, event_code, team_code, team_gender, team_place, points_dist_table, team_champs, team_minimum_age="0"):
        r = requests.post("https://rmsprodapi.nyrr.org/api/v2/awards/teamAwardRunners", headers=HEADERS, json={"eventCode": event_code, "teamCode": team_code, "teamGender": team_gender, "teamMinimumAge": team_minimum_age})
        
        retries = 1
        while r.status_code != 200:
            print(f"Request to NYRR Failed with Code {r.status_code}, Retrying in {5*retries}")
            time.sleep(5*retries)
            retries+=1
            r = requests.post("https://rmsprodapi.nyrr.org/api/v2/awards/teamAwardRunners", headers=HEADERS, json={"eventCode": event_code, "teamCode": team_code, "teamGender": team_gender, "teamMinimumAge": team_minimum_age})

        team_results = json.loads(r.content)['items']

        self._format_single_team_results(team_results, event_code, team_place, team_code, points_dist_table, team_champs)

        return team_results
    
    def _format_single_team_results(self, single_team_results, event_code, team_place, team_code, points_dist_table, team_champs):
        x=1
        team_points = POINTS_TABLE.get(str(team_place), 1)
        if team_champs:
            team_points = team_points * 2
        for result in single_team_results:
            result["team_place"] = team_place
            result["place_on_team"] = x
            result["team_code"] = team_code
            result["event_code"] = event_code
            result["points_scored"] = team_points * points_dist_table[str(x)]
            x+=1
    
    def scotland_2016(self, gender):
        if gender == "M":
            team_places = SCOT16_M_TABLE
        else:
            team_places = SCOT16_W_TABLE

        all_teams=[]
        for x in range(0, 5):
            r = requests.post("https://rmsprodapi.nyrr.org/api/v2/teams/search", headers=HEADERS, json={"eventCode":"SCOT16","searchWord":None,"pageIndex":x+1,"pageSize":51,"sortColumn":"TeamName","sortDescending":False})
            retries = 1
            while r.status_code != 200:
                print(f"Request to NYRR Failed with Code {r.status_code}, Retrying in {5*retries}")
                time.sleep(5*retries)
                retries+=1
                r = requests.post("https://rmsprodapi.nyrr.org/api/v2/teams/search", headers=HEADERS, json={"eventCode":"SCOT16","searchWord":None,"pageIndex":x+1,"pageSize":51,"sortColumn":"TeamName","sortDescending":False})
            all_teams.extend(json.loads(r.content)["items"])
        all_teams = [x for x in all_teams if x["runnersCount"] > 4]

        all_team_runners = []
        for team in all_teams:
            r = requests.post("https://rmsprodapi.nyrr.org/api/v2/teams/teamRunners", headers=HEADERS, json={"eventCode":"SCOT16","teamCode":team["teamCode"],"sortColumn":None,"sortDescending":False})
            retries = 1
            while r.status_code != 200:
                print(f"Request to NYRR Failed with Code {r.status_code}, Retrying in {5*retries}")
                time.sleep(5*retries)
                retries+=1
                r = requests.post("https://rmsprodapi.nyrr.org/api/v2/teams/teamRunners", headers=HEADERS, json={"eventCode":"SCOT16","teamCode":team["teamCode"],"sortColumn":None,"sortDescending":False})
            team_runners = json.loads(r.content)["items"]
            team_runners = [x for x in team_runners if x["gender"] == gender]
            if len(team_runners) >= 5:
                team_runners= team_runners[:5]
                self._format_single_team_results(team_runners, "SCOT16", team_places.get(team["teamCode"], 10), team["teamCode"], NORM_POINTS_DIST, False)
                all_team_runners.extend(team_runners)
            
        return all_team_runners
        