from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_movie_search():
    response = client.get('/api/movies', params={'q': 'Iron Man'})
    assert response.status_code == 200
    assert response.json()[0]['title'] == 'Iron Man'

def test_movie_records_include_real_source_and_image_metadata():
    movie = client.get('/api/movies', params={'q': 'Iron Man'}).json()[0]
    assert movie['source_url'].startswith('https://en.wikipedia.org/')
    assert movie['image_url'].startswith('https://')

def test_graph_qa_answers_director_question_from_real_records():
    response = client.post('/api/qa', json={'question': 'Who directed Inception?'})
    assert response.status_code == 200
    body = response.json()
    assert body['answer'] == 'Inception was directed by Christopher Nolan.'
    assert body['sources'][0]['title'] == 'Inception'

def test_cypher_endpoint_only_accepts_named_read_templates():
    response = client.post('/api/cypher', json={'template': 'drop_database'})
    assert response.status_code == 200
    assert response.json()['error'] == 'Unsupported read-only query template'
