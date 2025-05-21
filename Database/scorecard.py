# Final code of parsing HTML content of scorecard of a single match

import requests
from bs4 import BeautifulSoup
from pprint import pprint


headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(scorecard, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Each innings section
innings_divs = soup.select('div[id^="innings_"]')

all_teams_data = []

for inning in innings_divs:
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

    # Find all main blocks inside this innings
    blocks = inning.select("div.cb-col.cb-col-100.cb-ltst-wgt-hdr")

    for block in blocks:
        # Check if it's a batting block
        header = block.find("div", class_="cb-col cb-col-100 cb-scrd-sub-hdr cb-bg-gray")
        print(header)
        if header :
           header1 = header.find("div",class_="cb-col cb-col-25 text-bold")
           header2 = header.find("div",class_="cb-col cb-col-38 text-bold")
           if header1:
               header = header1
           else:
               header = header2
        print(header)
        if header and "BATTER" in header.text.upper():
            rows = block.find_all("div", class_="cb-col cb-col-100 cb-scrd-itms")
            for row in rows:
                name_tag = row.select_one("div.cb-col.cb-col-25 a")
                name = name_tag.text.strip() if name_tag else ""

                dismissal_tag = row.select_one("div.cb-col.cb-col-33")
                dismissal = dismissal_tag.text.strip() if dismissal_tag else ""

                stats = row.select("div.cb-col.cb-col-8.text-right, div.cb-col.cb-col-8.text-right.text-bold")
                if len(stats) >= 5:
                    runs = stats[0].text.strip()
                    balls = stats[1].text.strip()
                    fours = stats[2].text.strip()
                    sixes = stats[3].text.strip()
                    sr = stats[4].text.strip()
                    team_data["batting"].append({
                        "name": name,
                        "dismissal": dismissal,
                        "runs": runs,
                        "balls": balls,
                        "4s": fours,
                        "6s": sixes,
                        "SR": sr
                    })

        # Check if it's a bowling block
        elif header and "BOWLER" in header.text.upper():
            rows = block.find_all("div", class_="cb-col cb-col-100 cb-scrd-itms")
            for row in rows:
                name_tag = row.select_one("div.cb-col.cb-col-38 a")
                name = name_tag.text.strip() if name_tag else ""

                stats = row.select("div.cb-col.cb-col-8.text-right, div.cb-col.cb-col-8.text-right.text-bold,div.cb-col.cb-col-10.text-right")
                if len(stats) >= 6:
                    overs = stats[0].text.strip()
                    maidens = stats[1].text.strip()
                    runs = stats[2].text.strip()
                    wickets = stats[3].text.strip()
                    nb = stats[4].text.strip()
                    wd = stats[5].text.strip()
                    eco = stats[6].text.strip()

                    team_data["bowling"].append({
                        "name": name,
                        "overs": overs,
                        "maidens": maidens,
                        "runs": runs,
                        "wickets": wickets,
                        "economy": eco,
                        "no_ball": nb,
                        "wide":wd
                    })

    all_teams_data.append(team_data)

# ✅ Pretty print
for team in all_teams_data:
    print(f"\n=== {team['team']} | Score: {team['score']} ===\n")
    print(" Bowling:")
    pprint(team['bowling'])
    print(" Batting:")
    pprint(team['batting'])
