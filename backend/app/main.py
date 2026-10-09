import json
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Movie Graph API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "real_movies.json"
try:
    MOVIES = json.loads(DATA_PATH.read_text())["movies"]
except (FileNotFoundError, KeyError, json.JSONDecodeError):
    MOVIES = []

for movie in MOVIES:
    movie.setdefault(
        "image_url",
        "https://en.wikipedia.org/wiki/Special:FilePath/"
        + movie["title"].replace(" ", "_")
        + ".jpg",
    )

class GraphNode(BaseModel):
    id: str
    label: str
    kind: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "movie-graph-api"}

@app.get("/api/movies")
def movies(q: str | None = Query(default=None, max_length=80)):
    if not q:
        return MOVIES
    query = q.casefold()
    return [m for m in MOVIES if query in m["title"].casefold() or query in m["director"].casefold() or any(query in g.casefold() for g in m["genres"])]

@app.get("/api/movies/{movie_id}")
def movie(movie_id: str):
    return next((m for m in MOVIES if m["id"] == movie_id), {"detail": "Movie not found"})

@app.get("/api/graph")
def graph():
    node_map: dict[str, GraphNode] = {}
    edges: list[dict[str, str]] = []
    for item in MOVIES:
        movie_id = item["id"]
        node_map[movie_id] = GraphNode(id=movie_id, label=item["title"], kind="movie")
        for director in item["director"].split("; "):
            director_id = "director-" + director.lower().replace(" ", "-")
            node_map.setdefault(director_id, GraphNode(id=director_id, label=director, kind="person"))
            edges.append({"source": movie_id, "target": director_id, "type": "DIRECTED"})
        for genre in item["genres"]:
            genre_id = "genre-" + genre.lower().replace(" ", "-")
            node_map.setdefault(genre_id, GraphNode(id=genre_id, label=genre, kind="genre"))
            edges.append({"source": movie_id, "target": genre_id, "type": "HAS_GENRE"})
        group = item["group"]
        group_id = "group-" + group.lower().replace(" ", "-")
        node_map.setdefault(group_id, GraphNode(id=group_id, label=group, kind="genre"))
        edges.append({"source": movie_id, "target": group_id, "type": "PART_OF"})
    nodes = list(node_map.values())
    return {"nodes": nodes, "edges": edges}
