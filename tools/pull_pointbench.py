#!/usr/bin/env python3
"""Static pull of team rosters and the game schedule from Pointbench.

Writes data/pointbench.js (a script that sets window.POINTBENCH). Re-run only when rosters or fixtures change:
    python3 tools/pull_pointbench.py
Standard library only. Waits between requests.
"""
import datetime
import json
import re
import time
import urllib.request
from html import unescape
from html.parser import HTMLParser

BASE = "https://stats.pointbench.com/eu/eslcm/2026/index.php"
OUT = "data/pointbench.js"
HEADERS = {"User-Agent": "sixes-stat-tapper-pull/1.0"}
DELAY = 1.0  # seconds between requests


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


class RowParser(HTMLParser):
    """Collects every table row as a list of cells: {"cls", "text", "href"}."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = {"cls": a.get("class", ""), "text": "", "href": ""}
        elif tag == "a" and self.cell is not None:
            self.cell["href"] = unescape(a.get("href", ""))

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.cell["text"] = " ".join(self.cell["text"].split())
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell["text"] += data


def teamid_from(href):
    m = re.search(r"teamid=([a-z]+)", href)
    return m.group(1) if m else None


def gameid_from(href):
    m = re.search(r"gameid=(\d+)", href)
    return int(m.group(1)) if m else None


def main():
    index = fetch(BASE)
    team_ids = sorted(set(re.findall(r"teamid=([a-z]+)", index)))
    print("teams:", len(team_ids))

    teams, games = {}, {}
    for tid in team_ids:
        time.sleep(DELAY)
        p = RowParser()
        p.feed(fetch(f"{BASE}?cmd=team-schedule-stats&teamid={tid}"))

        roster = []
        for cells in p.rows:
            if len(cells) == 8 and cells[0]["cls"] == "cnt":
                roster.append({"number": cells[0]["text"], "name": cells[1]["text"]})

        for cells in p.rows:
            if len(cells) >= 8 and cells[0]["cls"] == "id":
                code = cells[0]["text"]
                gid = gameid_from(cells[7]["href"])
                key = str(gid) if gid else code
                games.setdefault(key, {
                    "code": code,
                    "gameId": gid,
                    "date": cells[2]["text"],
                    "time": cells[3]["text"],
                    "home": teamid_from(cells[4]["href"]),
                    "homeName": cells[4]["text"],
                    "away": teamid_from(cells[5]["href"]),
                    "awayName": cells[5]["text"],
                    "field": cells[6]["text"],
                    "result": cells[7]["text"],
                })

        teams[tid] = {"name": tid, "roster": roster}
        print(f"{tid}: {len(roster)} players")

    for g in games.values():
        if g["home"] in teams:
            teams[g["home"]]["name"] = g["homeName"]
        if g["away"] in teams:
            teams[g["away"]]["name"] = g["awayName"]

    out = {
        "pulled": datetime.date.today().isoformat(),
        "source": "https://stats.pointbench.com/eu/eslcm/2026/",
        "teams": teams,
        "games": sorted(games.values(), key=lambda g: g["code"]),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("window.POINTBENCH = ")
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write(";\n")
    print("games:", len(out["games"]), "->", OUT)


if __name__ == "__main__":
    main()
