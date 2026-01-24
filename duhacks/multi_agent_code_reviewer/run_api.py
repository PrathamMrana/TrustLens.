"""
Run Flask API Server
Entry point for the REST API backend
"""

from pathlib import Path
from dotenv import load_dotenv
from api.app import create_app
from utils.logger import Logger
import os

# Load .env file - search up the directory tree
def load_env_file():
    """Find and load .env file from current or parent directories"""
    current = Path(__file__).parent
    for _ in range(5):
        env_file = current / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return
        current = current.parent

# Find and load .env file
load_env_file()

# Create Flask app instance for production usage (e.g. Gunicorn)
app = create_app()

if __name__ == '__main__':
    logger = Logger("Server")
    logger.info("=" * 60)
    logger.info("Multi-Agent AI Code Review System - REST API")
    logger.info("=" * 60)
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info("=" * 60)
    logger.info("API Documentation: See API_DOCUMENTATION.md")
    logger.info("Health Check: http://localhost:5000/health")
    logger.info("API Base: http://localhost:5000/api")
    logger.info("=" * 60)
    
    # Run server
    app.run(host=host, port=port, debug=debug)
