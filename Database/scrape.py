from supabase import create_client
# from datetime import date
import re
# Supabase setup
url = "https://misdjojlogwqkaytsdcv.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pc2Rqb2psb2d3cWtheXRzZGN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc4ODc0MDAsImV4cCI6MjA2MzQ2MzQwMH0.2Lx8wjntdD-ndf8CVAjObfV-OfRw_GGoT9ZCzQAP3ac"
supabase = create_client(url, key)
winning_team = match_result.split(" won")[0].strip()

matchit = re.search(r'opt to (bat|bowl)', toss.lower())
toss_decision = matchit.group(1) if matchit else "N/A"

def parse_full_name(name):
    for player in players:
        if name in player:
             is_captain = "(c)" in player
             is_keeper = "(wk)" in player
             name = re.sub(r"\s*\((c|wk)\)", "", player).strip()
             return {
                "name": name,
                "is_captain": is_captain,
                "is_keeper": is_keeper
            }
def get_opponent(team_name):
    for team in all_teams_data:
         if not team_name in team['team']:
             return team['team']


def parse_dismissal(dismissal):
    dismissal = dismissal.lower().strip()
    result = {
        "type": None,
        "fielder": None,
        "bowler": None,
        "runner": None
    }

    # Not out
    if dismissal == "not out":
        result["type"] = "not out"

    # Run out (optional fielder in brackets)
    elif dismissal.startswith("run out"):
        result["type"] = "run out"
        fielder_match = re.search(r'run out\s*\(([^)]+)\)', dismissal)
        if fielder_match:
            result["fielder"] = fielder_match.group(1).strip().title()
 

    # Caught + bowled
    elif dismissal.startswith("c") and " b " in dismissal:
        result["type"] = "caught"
        match = re.search(r'c\s+(.+?)\s+b\s+(.+)', dismissal)
        if match:
            result["fielder"] = match.group(1).strip().title()
            result["bowler"] = match.group(2).strip().title()

    # Only bowled
    elif dismissal.startswith("b "):
        result["type"] = "bowled"
        result["bowler"] = dismissal[2:].strip().title()

    # LBW (assume bowled)
    elif dismissal.startswith("lbw b "):
        result["type"] = "lbw"
        result["bowler"] = dismissal[6:].strip().title()

    # Stumped
    elif dismissal.startswith("st") and " b " in dismissal:
        result["type"] = "stumped"
        match = re.search(r'st\s+(.+?)\s+b\s+(.+)', dismissal)
        if match:
            result["fielder"] = match.group(1).strip().title()
            result["bowler"] = match.group(2).strip().title()

    return result
team_runs = []

for team in all_teams_data:
    score_text = team['score']
    print(score_text)

    # Match formats like "174-8 (20 Ov)" or "177-3 (16.2 Ov)" or just "174"
    match = re.match(r"(\d+)-\d+\s+\([\d.]+\s+Ov\)", score_text)
    
    if match:
        runs = int(match.group(1))
        team_runs.append(runs)
        print("🏏 Runs:", runs)
    else:
        # Sometimes it's like "174" (e.g. all out without overs)
        match_simple = re.match(r"^(\d+)$", score_text)
        if match_simple:
            runs = int(match_simple.group(1))
            team_runs.append(runs)
            print("🏏 Runs (simple):", runs)
        else:
            print("❌ Could not parse runs:", score_text)

# if runs[0]>runs[1]:
# General data to be included in database 
print(team_runs)
win_info =""
if all_teams_data[0]['team'] == winning_team:
    win_info = "defending"
else:
    win_info= "chasing"
# print(date)
data={
    "Pitch_name":stadium,
    "match_date":match_date,
    "First_in_score":int(team_runs[0]),
    "Second_in_score":int(team_runs[1]),
    "Win":winning_team,
    "Win_info":win_info,
    "first_team_powerplay":int(powerplay_runs_list[0]),
    "second_team_powerplay":int(powerplay_runs_list[1]),
    "first_team":all_teams_data[0]['team'],
    "second_team":all_teams_data[1]['team'],
    "Toss":toss_decision
}
try:
    supabase.table("Pitch_data").insert(data).execute()
except Exception as e:
    print("❌ Error inserting Pitch_data:", data)
    print(e)
# bowler and batsman data to be included in database 
for team in all_teams_data:
    for batter in team['batting']:
        
        info = parse_full_name(batter["name"])
        if not info:
             continue
        player_name = info["name"]
        is_captain = info["is_captain"]
        is_keeper = info["is_keeper"]
        opponent_team =  get_opponent(team['team'])
        d_info = parse_dismissal(batter['dismissal'])
        win_team = 1
        if(team['team']!=winning_team):  win_team = 0
        data={
            "player_name": player_name,
            "player_team": team['team'],
            "role":"Batsman",
            "opponent":opponent_team ,
            "venue":stadium,
            "match_date":match_date,
            "runs": int(batter['runs']),
            "balls": int(batter['balls']),
            "fours": int(batter['4s']),
            "sixes": int(batter['6s']),
            "strike_rate": float(batter['SR']),
            "dismissal_type": d_info['type'],
            "dismissal_bowler":d_info['bowler'],
            "Team_win":int(win_team),
            "wicket_keeper":int(is_keeper),
            "captain":int(is_captain),
        }
        try:
         supabase.table("batsman_performances").insert(data).execute()
        except Exception as e:
            print("❌ Error inserting Pitch_data:", data)
            print(e)
        
    for bowler in team['bowling']:
        info = parse_full_name(bowler['name'])
        if not info:
             continue
        print(info)
        player_name = info["name"]
        is_captain = info["is_captain"]
        is_keeper = info["is_keeper"]
        opponent_team =  get_opponent(team['team'])
        win_team = 1
        if(team['team']!=winning_team):  win_team = 0
        data = {
          "player_name": player_name,
          "player_team":team['team'],
          "opponent":opponent_team,
          "venue":stadium,
          "overs":float(bowler['overs']),
          "maidens":int(bowler['maidens']),
          "runs_conceded":int(bowler['runs']),
          "wickets":int(bowler['wickets']),
          "economy":float(bowler['economy']),
          "wides":int(bowler['wide']),
          "match_date":match_date,
          "Team_win":int(win_team),
          "Captain":int(is_captain),
          "wicket_keeper":int(is_keeper)
        }
        supabase.table("bowler_performances").insert(data).execute()

