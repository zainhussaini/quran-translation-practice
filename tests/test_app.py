import pytest
from flaskr.app import app
from flaskr.data_reader import DatabaseReader

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_get(client):
    """Test the home route with GET method"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Quran Translation Practice' in response.data

def test_home_post(client):
    """Test the home route with POST method"""
    response = client.post('/', data={
        'surah': '2',
        'ayat': '255'
    })
    assert response.status_code == 200
    assert b'Quran Translation Practice' in response.data

def test_get_ayat_count(client):
    """Test getting ayat count for a surah"""
    response = client.get('/get_ayat_count/1')
    assert response.status_code == 200
    data = response.get_json()
    assert 'count' in data
    assert isinstance(data['count'], int)

def test_get_next_ayat_same_surah(client):
    """Test getting next ayat in the same surah"""
    response = client.get('/get_next_ayat/1/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['surah'] == 1
    assert data['ayat'] == 2

def test_get_next_ayat_next_surah(client):
    """Test getting first ayat of next surah"""
    with DatabaseReader() as db:
        last_ayat = db.get_ayat_count(1)
        response = client.get(f'/get_next_ayat/1/{last_ayat}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['surah'] == 2
        assert data['ayat'] == 1

def test_get_next_ayat_last_surah(client):
    """Test getting next ayat when at last surah"""
    response = client.get('/get_next_ayat/114/6')
    assert response.status_code == 200
    data = response.get_json()
    assert data['surah'] == 114
    assert data['ayat'] == 6 