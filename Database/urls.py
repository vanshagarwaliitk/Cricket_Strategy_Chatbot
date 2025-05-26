import pandas as pd
from bs4 import BeautifulSoup
import os 
import requests

base_url = "https://www.cricbuzz.com/cricket-scorecard-archives/"

# Generating a list of urls from base urls
urls = [f"{base_url}{year}" for year in range(2025,2007,-1)]
# print(urls)
print(len(urls))

#finding IPL series
new_urls = []
full_base = "https://www.cricbuzz.com"
for url in urls:
    webpage = requests.get(url)
    web = webpage.content
    soup = BeautifulSoup(web,"html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get("title", "")
        
        # Check for IPL 2016–2018 using title or href
        if "Indian Premier League" in title and "matches" in href:
            # if any(str(year) in title for year in range(2016, 2019)):
                full_url = full_base + href
                new_urls.append(full_url)
print(new_urls)

# Now finding all matches urls corresponding to one Ipl season
matches = []
for new_url in new_urls:
    wp = requests.get(new_url)
    sp = BeautifulSoup(wp.content,"html.parser")
    for tag in sp.find_all('a',class_="cb-text-complete"):
        href = tag.get('href')
        matches.append(f"https://www.cricbuzz.com{href}")

# finding scorecard url corresponding to each matches
scorecards =[]
for match in matches:
        scorecard =""
        if "/cricket-scores/" in match:
         parts = match.split("/cricket-scores/")
         scorecard = f"https://www.cricbuzz.com/live-cricket-scorecard/{parts[1]}"
        elif "/live-cricket-scores/" in match:
         parts = match.split("/live-cricket-scores/")
         scorecard = f"https://www.cricbuzz.com/live-cricket-scorecard/{parts[1]}"
        scorecards.append(scorecard)
print(len(scorecards))
print("first_scorecard",scorecards[0])
