# Unit Tests for Flask Application

import pytest
import json
from src.app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    """Test home endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert 'version' in data
    assert 'environment' in data
    assert 'timestamp' in data


def test_health(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'version' in data
    assert 'environment' in data


def test_ready(client):
    """Test readiness probe endpoint"""
    response = client.get('/ready')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'ready'


def test_metrics(client):
    """Test metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'request_count' in data
    assert 'error_count' in data
    assert 'version' in data


def test_get_users(client):
    """Test get all users endpoint"""
    response = client.get('/api/users')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]['name'] == 'John Doe'


def test_get_user_by_id(client):
    """Test get user by ID endpoint"""
    response = client.get('/api/users/1')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['id'] == 1
    assert data['name'] == 'John Doe'
    assert data['email'] == 'john@example.com'


def test_get_user_not_found(client):
    """Test get user with invalid ID"""
    response = client.get('/api/users/999')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data


def test_create_user(client):
    """Test create user endpoint"""
    new_user = {
        'name': 'Test User',
        'email': 'test@example.com'
    }
    
    response = client.post('/api/users',
                          data=json.dumps(new_user),
                          content_type='application/json')
    assert response.status_code == 201
    
    data = json.loads(response.data)
    assert data['name'] == 'Test User'
    assert data['email'] == 'test@example.com'


def test_create_user_invalid_data(client):
    """Test create user with invalid data"""
    invalid_user = {'name': 'Test User'}  # Missing email
    
    response = client.post('/api/users',
                          data=json.dumps(invalid_user),
                          content_type='application/json')
    assert response.status_code == 400


def test_info(client):
    """Test info endpoint"""
    response = client.get('/api/info')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'name' in data
    assert 'version' in data
    assert 'endpoints' in data
    assert isinstance(data['endpoints'], list)


def test_not_found(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data


def test_multiple_requests(client):
    """Test multiple requests to verify counter"""
    # Make several requests
    client.get('/')
    client.get('/api/users')
    client.get('/api/users/1')
    
    # Check metrics
    response = client.get('/metrics')
    data = json.loads(response.data)
    assert data['request_count'] >= 3
