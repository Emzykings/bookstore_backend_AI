import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_books(client):
    response = client.get('/api/books')
    assert response.status_code == 200
    assert b"books" in response.data

def test_get_book(client):
    response = client.get('/api/books/1')
    assert response.status_code == 200
    assert b"Book One" in response.data

def test_place_order(client):
    # First, log in to get the JWT token
    login_response = client.post('/login', json={"username": "test", "password": "test"})
    assert login_response.status_code == 200
    token = login_response.json['access_token']

    # Then, place an order with the token
    response = client.post('/api/orders', json={"book_id": 1, "quantity": 2}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert b"order" in response.data

def test_get_order_status(client):
    # First, log in to get the JWT token
    login_response = client.post('/login', json={"username": "test", "password": "test"})
    assert login_response.status_code == 200
    token = login_response.json['access_token']

    # Place an order to ensure there's an order to fetch
    client.post('/api/orders', json={"book_id": 1, "quantity": 2}, headers={"Authorization": f"Bearer {token}"})

    # Fetch the order status with the token
    response = client.get('/api/orders/1', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert b"order" in response.data