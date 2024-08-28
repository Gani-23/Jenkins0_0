# test_app.py
import pytest
from app import app  # Import your Flask app here

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_hello(client):
    """Test the /hello route."""
    response = client.get('/hello')
    assert response.status_code == 200
    assert b"Hello, I'm still alive!" in response.data
