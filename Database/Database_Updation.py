import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client
import re

url = "https://misdjojlogwqkaytsdcv.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pc2Rqb2psb2d3cWtheXRzZGN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc4ODc0MDAsImV4cCI6MjA2MzQ2MzQwMH0.2Lx8wjntdD-ndf8CVAjObfV-OfRw_GGoT9ZCzQAP3ac"
supabase = create_client(url, key)

for scorecard in scorecards:
    try:
        wp = requests.get(scorecard)
        sp = BeautifulSoup(wp.content, "html.parser")
        rows = sp.find_all("div", class_="cb-col cb-col-27")
        players = []
        stadium = []
        match_date = ""

        status_div = sp.find("div", class_="cb-min-stts") or sp.find("div", class_="cb-text-complete")
        match_result = status_div.text.strip() if status_div else ""

        toss = ""
        for row in rows:
            try:
                if "Date" in row.text:
                    parent = row.find_next_sibling("div", class_="cb-col cb-col-73")
                    timestamp = (parent.find("span")).get("timestamp")
                    dt = datetime.fromtimestamp(int(timestamp) / 1000)
                    match_date = dt.strftime("%Y-%m-%d")
                elif "Venue" in row.text:
                    stadium = row.find_next_sibling("div", class_="cb-col cb-col-73").text.strip()
                elif "Toss" in row.text:
                    toss = row.find_next_sibling("div", class_="cb-col cb-col-73").text.strip()
                elif "Playing" in row.text or "Bench" in row.text:
                    anchors = row.find_next_sibling("div", class_="cb-col cb-col-73").find_all("a")
                    for anchor in anchors:
                        name = anchor.text.strip()
                        if name:
                            players.append(name)
            except:
                continue

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(scorecard, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        powerplay_runs_list = []
        innings_divs = soup.select('div[id^="innings_"]')
        all_teams_data = []

        for inning in innings_divs:
            try:
                team_header = inning.select_one("div.cb-col.cb-col-100.cb-scrd-hdr-rw")
                if not team_header:
                    continue
                team_name = team_header.select_one("span")
                score = team_header.select_one("span.pull-right")
                if not team_name or not score:
                    continue

                team_data = {
                    "team": team_name.text.strip().replace(" Innings", ""),
                    "score": score.text.strip(),
                    "batting": [],
                    "bowling": []
                }

                blocks = inning.select("div.cb-col.cb-col-100.cb-ltst-wgt-hdr")
                for div in blocks:
                    try:
                        p = div.find_all("div", class_="cb-col cb-col-33 text-right")
                        if p:
                            powerplay_runs_list.append(p[1].text.strip())
                    except:
                        continue

                for block in blocks:
                    try:
                        header = block.find("div", class_="cb-col cb-col-100 cb-scrd-sub-hdr cb-bg-gray")
                        if header:
                            header = header.find("div", class_="cb-col cb-col-25 text-bold") or header.find("div", class_="cb-col cb-col-38 text-bold")

                        if header and "BATTER" in header.text.upper():
                            rows = block.find_all("div", class_="cb-col cb-col-100 cb-scrd-itms")
                            for row in rows:
                                try:
                                    name_tag = row.select_one("div.cb-col.cb-col-25 a")
                                    name = name_tag.text.strip() if name_tag else ""
                                    dismissal_tag = row.select_one("div.cb-col.cb-col-33")
                                    dismissal = dismissal_tag.text.strip() if dismissal_tag else ""
                                    stats = row.select("div.cb-col.cb-col-8.text-right, div.cb-col.cb-col-8.text-right.text-bold")
                                    if len(stats) >= 5:
                                        team_data["batting"].append({
                                            "name": name,
                                            "dismissal": dismissal,
                                            "runs": stats[0].text.strip(),
                                            "balls": stats[1].text.strip(),
                                            "4s": stats[2].text.strip(),
                                            "6s": stats[3].text.strip(),
                                            "SR": stats[4].text.strip()
                                        })
                                except:
                                    continue

                        elif header and "BOWLER" in header.text.upper():
                            rows = block.find_all("div", class_="cb-col cb-col-100 cb-scrd-itms")
                            for row in rows:
                                try:
                                    name_tag = row.select_one("div.cb-col.cb-col-38 a")
                                    name = name_tag.text.strip() if name_tag else ""
                                    stats = row.select("div.cb-col.cb-col-8.text-right, div.cb-col.cb-col-8.text-right.text-bold, div.cb-col.cb-col-10.text-right")
                                    if len(stats) >= 6:
                                        team_data["bowling"].append({
                                            "name": name,
                                            "overs": stats[0].text.strip(),
                                            "maidens": stats[1].text.strip(),
                                            "runs": stats[2].text.strip(),
                                            "wickets": stats[3].text.strip(),
                                            "no_ball": stats[4].text.strip(),
                                            "wide": stats[5].text.strip(),
                                            "economy": stats[6].text.strip() if len(stats) > 6 else ""
                                        })
                                except:
                                    continue
                    except:
                        continue

                all_teams_data.append(team_data)

            except:
                continue

        winning_team = ""
        try:
            winning_team = match_result.split(" won")[0].strip()
        except:
            pass

        try:
            matchit = re.search(r'opt to (bat|bowl)', toss.lower())
            toss_decision = matchit.group(1) if matchit else "N/A"
        except:
            toss_decision = "N/A"

        team_runs = []
        for team in all_teams_data:
            try:
                match = re.match(r"(\d+)-\d+\s+\([\d.]+\s+Ov\)", team['score'])
                if match:
                    team_runs.append(int(match.group(1)))
                else:
                    match_simple = re.match(r"^(\d+)$", team['score'])
                    if match_simple:
                        team_runs.append(int(match_simple.group(1)))
            except:
                continue

        try:
            win_info = "defending" if all_teams_data[0]['team'] == winning_team else "chasing"
            first_pp = int(powerplay_runs_list[0]) if len(powerplay_runs_list) > 0 else -1
            second_pp = int(powerplay_runs_list[1]) if len(powerplay_runs_list) > 1 else -1
            data = {
                "Pitch_name": stadium,
                "match_date": match_date,
                "First_in_score": int(team_runs[0]),
                "Second_in_score": int(team_runs[1]),
                "Win": winning_team,
                "Win_info": win_info,
                "first_team_powerplay": int(powerplay_runs_list[0]),
                "second_team_powerplay": int(powerplay_runs_list[1]),
                "first_team": all_teams_data[0]['team'],
                "second_team": all_teams_data[1]['team'],
                "Toss": toss_decision
            }
            supabase.table("Pitch_data").insert(data).execute()
        except Exception as e:
            print("❌ Error inserting Pitch_data:", e)

        for team in all_teams_data:
            for batter in team['batting']:
                try:
                    info = parse_full_name(batter["name"])
                    if not info:
                        continue
                    d_info = parse_dismissal(batter['dismissal'])
                    data = {
                        "player_name": info["name"],
                        "player_team": team['team'],
                        "role": "Batsman",
                        "opponent": get_opponent(team['team']),
                        "venue": stadium,
                        "match_date": match_date,
                        "runs": int(batter['runs']),
                        "balls": int(batter['balls']),
                        "fours": int(batter['4s']),
                        "sixes": int(batter['6s']),
                        "strike_rate": float(batter['SR']),
                        "dismissal_type": d_info['type'],
                        "dismissal_bowler": d_info['bowler'],
                        "Team_win": int(team['team'] == winning_team),
                        "wicket_keeper": int(info['is_keeper']),
                        "captain": int(info['is_captain'])
                    }
                    supabase.table("batsman_performances").insert(data).execute()
                except Exception as e:
                    print("❌ Error inserting batsman:", e)

            for bowler in team['bowling']:
                try:
                    info = parse_full_name(bowler["name"])
                    if not info:
                        continue
                    data = {
                        "player_name": info["name"],
                        "player_team": team['team'],
                        "opponent": get_opponent(team['team']),
                        "venue": stadium,
                        "overs": float(bowler['overs']),
                        "maidens": int(bowler['maidens']),
                        "runs_conceded": int(bowler['runs']),
                        "wickets": int(bowler['wickets']),
                        "economy": float(bowler['economy']),
                        "wides": int(bowler['wide']),
                        "match_date": match_date,
                        "Team_win": int(team['team'] == winning_team),
                        "Captain": int(info['is_captain']),
                        "wicket_keeper": int(info['is_keeper'])
                    }
                    supabase.table("bowler_performances").insert(data).execute()
                except Exception as e:
                    print("❌ Error inserting bowler:", e)

    except Exception as e:
        print("❌ Major failure for scorecard:", scorecard)
        print(e)
