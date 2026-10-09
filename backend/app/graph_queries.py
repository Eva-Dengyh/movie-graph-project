"""Safe, read-only Cypher templates for deterministic graph questions."""

DIRECTOR_QUERY = """
MATCH (m:Movie)-[:DIRECTED]->(p:Person {name: $director})
RETURN m ORDER BY m.year DESC
""".strip()

MOVIE_CONTEXT_QUERY = """
MATCH (m:Movie {id: $movie_id})
OPTIONAL MATCH (m)-[r:DIRECTED|HAS_GENRE|PART_OF]->(n)
RETURN m, collect({type: type(r), node: n}) AS relations
""".strip()

PATH_QUERY = """
MATCH path = (a)-[*1..3]-(b)
WHERE coalesce(a.name, a.title) = $start AND coalesce(b.name, b.title) = $end
RETURN path ORDER BY length(path) LIMIT $limit
""".strip()

def supported_templates() -> dict[str, str]:
    return {"director_movies": DIRECTOR_QUERY, "movie_context": MOVIE_CONTEXT_QUERY, "find_path": PATH_QUERY}

