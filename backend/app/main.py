from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Movie Graph API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

MOVIES = [
    {"id": "dune", "title": "Dune", "year": 2021, "director": "Denis Villeneuve", "genres": ["Sci-Fi", "Adventure"]},
    {"id": "blade-runner-2049", "title": "Blade Runner 2049", "year": 2017, "director": "Denis Villeneuve", "genres": ["Sci-Fi"]},
    {"id": "arrival", "title": "Arrival", "year": 2016, "director": "Denis Villeneuve", "genres": ["Sci-Fi", "Drama"]},
]

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
    nodes = [GraphNode(id="dune", label="Dune", kind="movie"), GraphNode(id="villeneuve", label="Denis Villeneuve", kind="person")]
    return {"nodes": nodes, "edges": [{"source": "dune", "target": "villeneuve", "type": "DIRECTED"}]}
