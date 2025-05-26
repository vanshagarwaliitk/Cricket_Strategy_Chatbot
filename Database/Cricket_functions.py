import re
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

