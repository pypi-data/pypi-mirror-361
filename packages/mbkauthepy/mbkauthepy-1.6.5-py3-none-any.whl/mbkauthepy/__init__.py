import logging
import os
from pathlib import Path
from flask import Flask, render_template, url_for
from werkzeug.exceptions import HTTPException
from flask_cors import CORS

# --- Exports ---
__all__ = [
    "validate_session",
    "check_role_permission",
    "validate_session_and_role",
    "authenticate_token",
    "mbkauthe_bp",
    "configure_mbkauthe",
    "get_cookie_options"
]


def configure_mbkauthe(app: Flask):
    """
    Configures mbkauthe components (config, routes, error handler) for the Flask app.
    """
    from .config import configure_flask_app
    from .routes import mbkauthe_bp

    logger = logging.getLogger(__name__)
    logger.info("Configuring mbkauthe base components for Flask app...")

    configure_flask_app(app)
    app.register_blueprint(mbkauthe_bp)
    logger.info("mbkauthe API blueprint registered.")

    # Get package template directory
    package_dir = Path(__file__).parent
    package_template_path = package_dir / 'templates'


    # Add package templates first (lower priority)
    if package_template_path.exists():
        app.jinja_loader.searchpath.append(str(package_template_path))
        logger.info(f"Added package template directory: {package_template_path}")

    # Error handler remains the same
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        try:
            home_url = url_for('home') if 'home' in app.view_functions else '/'
            return render_template(
                "error.html",
                code=error.code,
                name=error.name,
                message=error.description,
                page_url=home_url,
                page_name="home"
            ), error.code
        except Exception as e:
            logger.error(f"Error rendering error template: {str(e)}")
            return f"Error {error.code}: {error.name}", error.code

    logger.info("mbkauthe base configuration complete.")
# --- Import items needed for export AFTER the function definition ---
from .middleware import (
    validate_session,
    check_role_permission,
    validate_session_and_role,
    authenticate_token,
)
from .routes import mbkauthe_bp
from .utils import get_cookie_options