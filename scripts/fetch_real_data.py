"""Fetch a reproducible first movie dataset from public Wikipedia summaries.

The credit/group mapping is intentionally explicit and reviewable; summaries and
source metadata are fetched from Wikipedia at runtime and never invented by the UI.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "real_movies.json"
UA = "movie-graph-project/0.1 (public-data-research)"

MOVIES = [
    # Marvel Cinematic Universe
    ("Iron Man", "Iron Man", 2008, "Jon Favreau", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    ("The Incredible Hulk", "The Incredible Hulk", 2008, "Louis Leterrier", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    ("Iron Man 2", "Iron Man 2", 2010, "Jon Favreau", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    ("Thor", "Thor (film)", 2011, "Kenneth Branagh", "Marvel Cinematic Universe", ["Action", "Fantasy"]),
    ("Captain America: The First Avenger", "Captain America: The First Avenger", 2011, "Joe Johnston", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    ("The Avengers", "The Avengers (2012 film)", 2012, "Joss Whedon", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    ("Guardians of the Galaxy", "Guardians of the Galaxy (film)", 2014, "James Gunn", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    ("Black Panther", "Black Panther (film)", 2018, "Ryan Coogler", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    ("Avengers: Infinity War", "Avengers: Infinity War", 2018, "Anthony Russo; Joe Russo", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    ("Avengers: Endgame", "Avengers: Endgame", 2019, "Anthony Russo; Joe Russo", "Marvel Cinematic Universe", ["Action", "Science Fiction"]),
    # Christopher Nolan
    ("Following", "Following", 1998, "Christopher Nolan", "Christopher Nolan", ["Crime", "Thriller"]),
    ("Memento", "Memento (film)", 2000, "Christopher Nolan", "Christopher Nolan", ["Mystery", "Thriller"]),
    ("Batman Begins", "Batman Begins", 2005, "Christopher Nolan", "Christopher Nolan", ["Action", "Superhero"]),
    ("The Dark Knight", "The Dark Knight", 2008, "Christopher Nolan", "Christopher Nolan", ["Action", "Superhero"]),
    ("Inception", "Inception", 2010, "Christopher Nolan", "Christopher Nolan", ["Science Fiction", "Thriller"]),
    ("The Dark Knight Rises", "The Dark Knight Rises", 2012, "Christopher Nolan", "Christopher Nolan", ["Action", "Superhero"]),
    ("Interstellar", "Interstellar (film)", 2014, "Christopher Nolan", "Christopher Nolan", ["Science Fiction", "Drama"]),
    ("Dunkirk", "Dunkirk (2017 film)", 2017, "Christopher Nolan", "Christopher Nolan", ["War", "Drama"]),
    ("Tenet", "Tenet (film)", 2020, "Christopher Nolan", "Christopher Nolan", ["Science Fiction", "Action"]),
    ("Oppenheimer", "Oppenheimer (film)", 2023, "Christopher Nolan", "Christopher Nolan", ["Biography", "Drama"]),
    # Stephen Chow
    ("From Beijing with Love", "From Beijing with Love", 1994, "Stephen Chow; Lee Lik-chi", "Stephen Chow", ["Comedy", "Action"]),
    ("A Chinese Odyssey Part One: Pandora's Box", "A Chinese Odyssey Part One: Pandora's Box", 1995, "Jeffrey Lau", "Stephen Chow", ["Comedy", "Fantasy"]),
    ("A Chinese Odyssey Part Two: Cinderella", "A Chinese Odyssey Part Two: Cinderella", 1995, "Jeffrey Lau", "Stephen Chow", ["Comedy", "Fantasy"]),
    ("The God of Cookery", "The God of Cookery", 1996, "Stephen Chow; Lee Lik-chi", "Stephen Chow", ["Comedy"]),
    ("Shaolin Soccer", "Shaolin Soccer", 2001, "Stephen Chow", "Stephen Chow", ["Comedy", "Sports"]),
    ("Kung Fu Hustle", "Kung Fu Hustle", 2004, "Stephen Chow", "Stephen Chow", ["Comedy", "Action"]),
    ("CJ7", "CJ7", 2008, "Stephen Chow", "Stephen Chow", ["Comedy", "Science Fiction"]),
    ("Journey to the West: Conquering the Demons", "Journey to the West: Conquering the Demons", 2013, "Stephen Chow; Derek Kwok", "Stephen Chow", ["Comedy", "Fantasy"]),
    ("The Mermaid", "The Mermaid (2016 film)", 2016, "Stephen Chow", "Stephen Chow", ["Comedy", "Fantasy"]),
]

def fetch(title: str) -> dict:
    encoded = urllib.parse.quote(title.replace(" ", "_"), safe="_():'")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def main() -> None:
    records = []
    fetched_at = datetime.now(UTC).isoformat()
    for display, page, year, director, group, genres in MOVIES:
        try:
            summary = fetch(page)
            records.append({
                "id": f"wiki-{page.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(':', '')}",
                "title": display,
                "year": year,
                "director": director,
                "group": group,
                "genres": genres,
                "summary": summary.get("extract", ""),
                "source_url": summary.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{page.replace(' ', '_')}"),
                "source_title": summary.get("title", page),
                "fetched_at": fetched_at,
            })
            print(f"fetched: {display}")
        except Exception as exc:
            print(f"skipped: {display}: {exc}")
        time.sleep(0.35)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"source": "Wikipedia REST API", "fetched_at": fetched_at, "movies": records}, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {len(records)} records to {OUT}")

if __name__ == "__main__":
    main()
