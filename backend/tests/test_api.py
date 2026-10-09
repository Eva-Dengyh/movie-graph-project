from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_movie_search():
    response = client.get('/api/movies', params={'q': 'Iron Man'})
    assert response.status_code == 200
    assert response.json()[0]['title'] == 'Iron Man'
