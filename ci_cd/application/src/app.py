# Sample Python Flask Application for CI/CD Pipeline

from flask import Flask, jsonify, request
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['VERSION'] = os.getenv('APP_VERSION', '1.0.0')
app.config['ENVIRONMENT'] = os.getenv('APP_ENV', 'development')

# Metrics
request_count = 0
error_count = 0


@app.route('/')
def home():
    """Home endpoint"""
    global request_count
    request_count += 1
    
    return jsonify({
        'message': 'Welcome to CI/CD Pipeline Demo Application',
        'version': app.config['VERSION'],
        'environment': app.config['ENVIRONMENT'],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health')
def health():
    """Health check endpoint for Kubernetes probes"""
    return jsonify({
        'status': 'healthy',
        'version': app.config['VERSION'],
        'environment': app.config['ENVIRONMENT']
    }), 200


@app.route('/ready')
def ready():
    """Readiness probe endpoint"""
    # Add any startup checks here
    return jsonify({
        'status': 'ready',
        'version': app.config['VERSION']
    }), 200


@app.route('/metrics')
def metrics():
    """Basic metrics endpoint for Prometheus"""
    return jsonify({
        'request_count': request_count,
        'error_count': error_count,
        'version': app.config['VERSION'],
        'environment': app.config['ENVIRONMENT']
    })


@app.route('/api/users', methods=['GET'])
def get_users():
    """Sample API endpoint - Get users"""
    global request_count
    request_count += 1
    
    users = [
        {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
        {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
        {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com'}
    ]
    
    logger.info(f"Fetched {len(users)} users")
    return jsonify(users)


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Sample API endpoint - Get user by ID"""
    global request_count
    request_count += 1
    
    users = {
        1: {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
        2: {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
        3: {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com'}
    }
    
    user = users.get(user_id)
    if user:
        logger.info(f"Fetched user {user_id}")
        return jsonify(user)
    else:
        logger.warning(f"User {user_id} not found")
        global error_count
        error_count += 1
        return jsonify({'error': 'User not found'}), 404


@app.route('/api/users', methods=['POST'])
def create_user():
    """Sample API endpoint - Create user"""
    global request_count
    request_count += 1
    
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        global error_count
        error_count += 1
        return jsonify({'error': 'Invalid data'}), 400
    
    new_user = {
        'id': 4,
        'name': data['name'],
        'email': data['email']
    }
    
    logger.info(f"Created user: {new_user}")
    return jsonify(new_user), 201


@app.route('/api/info')
def info():
    """Application information endpoint"""
    return jsonify({
        'name': 'CI/CD Demo Application',
        'version': app.config['VERSION'],
        'environment': app.config['ENVIRONMENT'],
        'python_version': os.sys.version,
        'endpoints': [
            '/',
            '/health',
            '/ready',
            '/metrics',
            '/api/users',
            '/api/users/<id>',
            '/api/info'
        ]
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    global error_count
    error_count += 1
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    global error_count
    error_count += 1
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting application on port {port}")
    logger.info(f"Environment: {app.config['ENVIRONMENT']}")
    logger.info(f"Version: {app.config['VERSION']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
