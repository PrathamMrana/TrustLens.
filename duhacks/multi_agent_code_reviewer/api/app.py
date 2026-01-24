"""
Flask REST API Application
Main Flask app for Multi-Agent Code Review System
"""

from flask import Flask
from flask_cors import CORS
from api.routes import api_blueprint
from utils.logger import Logger
import os


def create_app(config=None):
    """
    Application factory for Flask app.
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Initialize logger
    logger = Logger("FlaskApp")
    logger.info("Multi-Agent Code Review API initialized")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            "status": "healthy",
            "service": "Multi-Agent Code Review System",
            "version": "1.0.0"
        }, 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return {
            "message": "Multi-Agent Code Review System API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "analyze": "/api/analyze",
                "status": "/api/status/<job_id>",
                "reports": "/api/reports/<job_id>"
            }
        }, 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
