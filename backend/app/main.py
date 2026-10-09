import json
import re
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .neo4j_store import Neo4jStore
from .graph_queries import DIRECTOR_QUERY, MOVIE_CONTEXT_QUERY, PATH_QUERY

app = FastAPI(title="Movie Graph API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "real_movies.json"
try:
    MOVIES = json.loads(DATA_PATH.read_text())["movies"]
except (FileNotFoundError, KeyError, json.JSONDecodeError):
    MOVIES = []

GRAPH_STORE = Neo4jStore()

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

class Question(BaseModel):
    question: str

class CypherRequest(BaseModel):
    template: str
    params: dict[str, str | int] = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "movie-graph-api", "neo4j": GRAPH_STORE.available}

@app.get("/api/storage")
def storage():
    return {"backend": "neo4j" if GRAPH_STORE.available else "json-fallback", "neo4j": GRAPH_STORE.available}

@app.post("/api/cypher")
def cypher(request: CypherRequest):
    templates = {"director_movies": DIRECTOR_QUERY, "movie_context": MOVIE_CONTEXT_QUERY, "find_path": PATH_QUERY}
    if request.template not in templates:
        return {"error": "Unsupported read-only query template"}
    if not GRAPH_STORE.available:
        return {"backend": "json-fallback", "rows": []}
    return {"backend": "neo4j", "rows": GRAPH_STORE.run(templates[request.template], request.params)}

@app.get("/api/movies")
def movies(q: str | None = Query(default=None, max_length=80)):
    if not q:
        return MOVIES
    query = q.casefold()
    return [m for m in MOVIES if query in m["title"].casefold() or query in m["director"].casefold() or any(query in g.casefold() for g in m["genres"])]

@app.get("/api/movies/{movie_id}")
def movie(movie_id: str):
    return next((m for m in MOVIES if m["id"] == movie_id), {"detail": "Movie not found"})

@app.post("/api/qa")
def graph_qa(payload: Question):
    question = payload.question.strip()
    normalized = question.casefold()
    if any(word in normalized for word in ("who directed", "director of", "导演")):
        match = next((m for m in MOVIES if m["title"].casefold() in normalized), None)
        if match:
            return {"answer": f"{match['title']} was directed by {match['director']}.", "intent": "movie_director", "sources": [match]}
    if any(word in normalized for word in ("what movies", "which films", "作品", "拍了哪些")):
        director = next((m["director"] for m in MOVIES if m["director"].casefold() in normalized), None)
        if director:
            matches = [m for m in MOVIES if director.casefold() in m["director"].casefold()]
            return {"answer": f"{director} is linked to {len(matches)} films in this graph.", "intent": "director_movies", "sources": matches}
    if any(word in normalized for word in ("genre", "类型", "属于什么")):
        match = next((m for m in MOVIES if m["title"].casefold() in normalized), None)
        if match:
            return {"answer": f"{match['title']} is tagged as {', '.join(match['genres'])}.", "intent": "movie_genres", "sources": [match]}
    if any(word in normalized for word in ("universe", "group", "宇宙", "系列")):
        match = next((m for m in MOVIES if m["title"].casefold() in normalized), None)
        if match:
            return {"answer": f"{match['title']} belongs to {match['group']}.", "intent": "movie_group", "sources": [match]}
    return {"answer": "I could not map that question to a supported graph query yet.", "intent": "unsupported", "sources": [], "supported_queries": ["Who directed Inception?", "What movies did Christopher Nolan direct?", "What genre is Dune?"]}

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
