# Movie Graph Project

Interactive movie knowledge graph and GraphRAG-ready exploration workspace.

## Architecture

- `frontend/`: Vite + React + TypeScript single-page application.
- `backend/`: FastAPI service with a clean graph repository boundary.
- `infra/`: Neo4j service configuration.
- `scripts/fetch_real_data.py`: reproducible public-data fetcher for the first real dataset.

## MVP

- Responsive relationship graph for movies, people, genres and franchises.
- Search and node focus.
- Movie detail panel and relationship path preview.
- FastAPI endpoints ready to switch from demo data to Neo4j.
- 29 real film records fetched from public Wikipedia page summaries, covering the MCU, Christopher Nolan, and Stephen Chow.
- No login or favorites in v1.

## Run

```bash
docker compose -f infra/docker-compose.yml up --build
```

Then open `http://localhost:5173`.

Refresh the public dataset:

```bash
python3 scripts/fetch_real_data.py
```

The generated `data/real_movies.json` keeps the source URL, source title, fetch timestamp, summary, year, director, group, and genres for every record. The first pass uses Wikipedia REST summaries with an explicit, reviewable credit/group mapping; it does not claim to be a complete filmography or replace a production knowledge graph.

For frontend-only development:

```bash
cd frontend
npm install
npm run dev
```

For backend development:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
