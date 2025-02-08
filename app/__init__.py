from flask import Flask
from config.settings import FLASK_DEBUG
from config.logging_config import logger

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configurations
    app.config["DEBUG"] = FLASK_DEBUG

    # Register blueprints (if any)
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    logger.info("Flask application initialized successfully.")
    
    return app
