# Movie Graph Project

Interactive movie knowledge graph and GraphRAG-ready exploration workspace.

## Architecture

- `frontend/`: Vite + React + TypeScript single-page application.
- `backend/`: FastAPI service with a clean graph repository boundary.
- `infra/`: Neo4j service configuration.

## MVP

- Responsive relationship graph for movies, people, genres and franchises.
- Search and node focus.
- Movie detail panel and relationship path preview.
- FastAPI endpoints ready to switch from demo data to Neo4j.
- No login or favorites in v1.

## Run

```bash
docker compose -f infra/docker-compose.yml up --build
```

Then open `http://localhost:5173`.

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
