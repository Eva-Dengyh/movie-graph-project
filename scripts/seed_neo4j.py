"""Idempotently load the real movie dataset into Neo4j."""
import json, os
from pathlib import Path
from neo4j import GraphDatabase

root = Path(__file__).resolve().parents[1]
movies = json.loads((root / "data/real_movies.json").read_text())["movies"]
for movie in movies:
    movie.setdefault("image_url", "https://en.wikipedia.org/wiki/Special:FilePath/" + movie["title"].replace(" ", "_") + ".jpg")
driver = GraphDatabase.driver(os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"), auth=(os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD", "moviegraphdev")))
with driver.session() as session:
    session.run("MATCH (p:Person)-[r:DIRECTED]->(m:Movie) DELETE r")
    session.run("CREATE CONSTRAINT movie_id IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE")
    session.run("CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE")
    session.run("CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE")
    session.run("CREATE CONSTRAINT universe_name IF NOT EXISTS FOR (u:Universe) REQUIRE u.name IS UNIQUE")
    for movie in movies:
        session.run("""
        MERGE (m:Movie {id: $id}) SET m.title=$title, m.year=$year, m.summary=$summary, m.source_url=$source_url, m.image_url=$image_url
        WITH m
        UNWIND split($directors, '; ') AS director
        MERGE (p:Person {name: director}) MERGE (m)-[:DIRECTED]->(p)
        WITH m
        UNWIND $genres AS genre
        MERGE (g:Genre {name: genre}) MERGE (m)-[:HAS_GENRE]->(g)
        WITH m
        MERGE (u:Universe {name: $group}) MERGE (m)-[:PART_OF]->(u)
        """, **movie, directors=movie["director"])
driver.close()
print(f"seeded {len(movies)} movies")
