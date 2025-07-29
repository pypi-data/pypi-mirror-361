# mbkauthepy/__init__.py

import logging
from flask import Flask, render_template, url_for
from werkzeug.exceptions import HTTPException
from pathlib import Path
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


# --- Setup Function ---
def configure_mbkauthe(app: Flask):
    """
    Configures mbkauthe components (config, routes, error handler) for the Flask app.

    Args:
        app (Flask): The Flask application instance.
    """
    from .config import configure_flask_app
    from .routes import mbkauthe_bp

    logger = logging.getLogger(__name__)
    logger.info("Configuring mbkauthe base components for Flask app...")

    configure_flask_app(app)
    app.register_blueprint(mbkauthe_bp)
    logger.info("mbkauthe API blueprint registered.")

    # Register the Global Error Handler
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """
        Catches all HTTP exceptions and renders our single error page.
        """
        # ==================================================================
        #  FIXED SECTION
        # ==================================================================
        # Check if the 'home' endpoint is registered before trying to build a URL for it.
        # The correct way is to check the app's view_functions dictionary.
        template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ code }} - {{ name }}</title>
            <link rel="icon" type="image/x-icon" href="https://mbktechstudio.com/Assets/Images/Icon/dgicon.svg">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                :root {
                  --primary: #4361ee;
                  --primary-dark: #3a0ca3;
                  --primary-light: rgba(67, 97, 238, 0.1);
                  --secondary: #f72585;
                  --secondary-light: rgba(247, 37, 133, 0.1);
                  --dark: #121212;
                  --dark-light: #1e1e1e;
                  --darker: #0a0a0a;
                  --light: #f8f9fa;
                  --lighter: #ffffff;
                  --gray: #cccccc;
                  --gray-dark: #888888;
                  --success: #4cc9f0;
                  --warning: #f8961e;
                  --danger: #ef233c;
                  --gradient: linear-gradient(135deg, var(--primary), var(--secondary));
                  --glass: rgba(30, 30, 30, 0.5);
                  --glass-border: rgba(255, 255, 255, 0.1);
                  --transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.1);
                  --shadow-sm: 0 4px 6px rgba(0, 0, 0, 0.1);
                  --shadow-md: 0 8px 30px rgba(0, 0, 0, 0.2);
                  --shadow-lg: 0 15px 40px rgba(0, 0, 0, 0.3);
                  --radius-sm: 8px;
                  --radius-md: 12px;
                  --radius-lg: 16px;
                  --radius-xl: 24px;
                }

                * {
                  margin: 0;
                  padding: 0;
                  box-sizing: border-box;
                  font-family: 'Poppins', sans-serif;
                }

                body {
                  background: var(--dark);
                  color: var(--light);
                  line-height: 1.6;
                  min-height: 100vh;
                  display: flex;
                  flex-direction: column;
                }

                header {
                  position: fixed;
                  top: 0;
                  left: 0;
                  width: 100%;
                  z-index: 1000;
                  transition: var(--transition);
                  background: linear-gradient(to bottom, rgba(10, 10, 10, 0.9), rgba(10, 10, 10, 0.7));
                  backdrop-filter: blur(10px);
                  border-bottom: 1px solid var(--glass-border);
                }

                nav {
                  padding: 10px 5%;
                  max-width: 1400px;
                  margin: 0 auto;
                }

                .navbar {
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                }

                .logo {
                  display: flex;
                  align-items: center;
                  gap: 10px;
                }

                .logo img {
                  height: 30px;
                  width: auto;
                  transition: var(--transition);
                }

                .logo:hover img {
                  transform: rotate(15deg);
                }

                .logo-text {
                  font-size: 1.8rem;
                  font-weight: 700;
                  background: var(--gradient);
                  -webkit-background-clip: text;
                  background-clip: text;
                  color: transparent;
                }

                .status-container {
                  flex: 1;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 120px 5% 80px;
                  position: relative;
                  overflow: hidden;
                  background: radial-gradient(circle at 70% 20%, rgba(67, 97, 238, 0.15), transparent 60%);
                }

                .status-box {
                  background: var(--dark-light);
                  border-radius: var(--radius-xl);
                  padding: 2.5rem;
                  width: 100%;
                  max-width: 600px;
                  box-shadow: var(--shadow-lg);
                  border: 1px solid var(--glass-border);
                  text-align: center;
                  position: relative;
                  z-index: 2;
                  transition: var(--transition);
                }

                .status-box:hover {
                  transform: translateY(-5px);
                  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
                }

                .status-code {
                  font-size: 5rem;
                  font-weight: 700;
                  color: var(--danger);
                  margin-bottom: 1.5rem;
                  position: relative;
                }

                .status-code::after {
                  content: '';
                  position: absolute;
                  bottom: -15px;
                  left: 50%;
                  transform: translateX(-50%);
                  width: 80px;
                  height: 4px;
                  background: var(--gradient);
                  border-radius: 2px;
                }

                .status-name {
                  font-size: 2rem;
                  color: var(--lighter);
                  font-weight: 600;
                  margin-bottom: 1rem;
                }

                .status-message {
                  font-size: 1.1rem;
                  color: var(--gray);
                  margin-bottom: 2rem;
                }

                .status-link {
                  display: inline-block;
                  padding: 12px 25px;
                  background: var(--primary);
                  color: white;
                  text-decoration: none;
                  border-radius: 8px;
                  font-weight: 500;
                  transition: var(--transition);
                  margin-top: 1rem;
                }

                .status-link:hover {
                  background: var(--primary-dark);
                  transform: translateY(-2px);
                  box-shadow: var(--shadow-md);
                }

                .status-element {
                  position: absolute;
                  opacity: 0.1;
                  z-index: 1;
                  animation: float 6s ease-in-out infinite;
                }

                .status-element:nth-child(1) {
                  top: 20%;
                  left: 10%;
                  font-size: 5rem;
                  animation-delay: 0s;
                }

                .status-element:nth-child(2) {
                  top: 60%;
                  left: 80%;
                  font-size: 4rem;
                  animation-delay: 1s;
                }

                .status-element:nth-child(3) {
                  top: 30%;
                  left: 70%;
                  font-size: 3rem;
                  animation-delay: 2s;
                }

                .status-element:nth-child(4) {
                  top: 80%;
                  left: 20%;
                  font-size: 6rem;
                  animation-delay: 3s;
                }

                @keyframes float {
                  0%, 100% {
                    transform: translateY(0) rotate(0deg);
                  }
                  50% {
                    transform: translateY(-20px) rotate(5deg);
                  }
                }

                .details-wrapper {
                  margin-top: 2rem;
                  background: var(--dark-light);
                  border-radius: var(--radius-md);
                  padding: 1.5rem;
                  box-shadow: var(--shadow-md);
                  cursor: pointer;
                  transition: var(--transition);
                }

                .details-header {
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  color: var(--lighter);
                  font-size: 1rem;
                }

                .details-header i {
                  transition: var(--transition);
                }

                .details-wrapper:hover {
                  background: var(--darker);
                }

                .error-details-wrapper {
                  display: none;
                  margin-top: 1rem;
                }

                .details-wrapper.active .error-details-wrapper {
                  display: block;
                }

                .error-details {
                  width: 100%;
                  height: 150px;
                  background: var(--darker);
                  border: 1px solid var(--glass-border);
                  border-radius: var(--radius-sm);
                  color: var(--light);
                  padding: 1rem;
                  resize: none;
                  font-size: 0.9rem;
                  font-family: monospace;
                }

                .copy-btn {
                  margin-top: 0.5rem;
                  background: var(--primary);
                  color: var(--lighter);
                  border: none;
                  border-radius: var(--radius-sm);
                  padding: 0.5rem 1rem;
                  cursor: pointer;
                  transition: var(--transition);
                  font-size: 0.9rem;
                }

                .copy-btn:hover {
                  background: var(--primary-dark);
                }

                @media (max-width: 768px) {
                  .status-code {
                    font-size: 4rem;
                  }
                  .status-name {
                    font-size: 1.8rem;
                  }
                  .status-message {
                    font-size: 1rem;
                  }
                }
            </style>
        </head>
        <body>
            <header>
                <nav>
                    <div class="navbar">
                        <a class="logo">
                            <img src="https://mbktechstudio.com/Assets/Images/Icon/dgicon.svg" alt="MBK Tech Studio Logo">
                            <span class="logo-text">MBK Authe</span>
                        </a>
                    </div>
                </nav>
            </header>

            <section class="status-container">
                <i class="fas fa-server status-element"></i>
                <i class="fas fa-database status-element"></i>
                <i class="fas fa-network-wired status-element"></i>
                <i class="fas fa-code status-element"></i>

                <div class="status-box">
                    <h1 class="status-code">{{ code }}</h1>
                    <h2 class="status-name">{{ name }}</h2>
                    <p class="status-message">{{ message }}</p>

                    {% if code == 401 %}
                        <a href="{{ url_for('mbkauthe.login_page') }}" class="status-link">Go to Login Page</a>
                    {% else %}
                                <a href="{{ page_url }}" class="status-link">Go to {{ page_name }}</a>
                    {% endif %}

                    {% if details %}
                    <div class="details-wrapper" onclick="toggleDetailsDropdown(this)">
                        <div class="details-header">
                            <span>Show Error Details</span>
                            <i class="fas fa-chevron-down"></i>
                        </div>
                        <div class="error-details-wrapper">
                            <textarea class="error-details" id="errorDetails" readonly>{{ details }}</textarea>
                            <button class="copy-btn" type="button" aria-label="Copy error details"
                                onclick="copyErrorDetails(this); event.stopPropagation();">
                                <i class="fas fa-copy"></i> Copy
                            </button>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </section>

            <script>
                function toggleDetailsDropdown(element) {
                    element.classList.toggle('active');
                    const icon = element.querySelector('.details-header i');
                    if (element.classList.contains('active')) {
                        icon.style.transform = 'rotate(180deg)';
                    } else {
                        icon.style.transform = 'rotate(0deg)';
                    }
                }

                function copyErrorDetails(button) {
                    const details = button.previousElementSibling.value;
                    navigator.clipboard.writeText(details).then(() => {
                        const originalText = button.innerHTML;
                        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        setTimeout(() => {
                            button.innerHTML = originalText;
                        }, 2000);
                    }).catch(err => {
                        console.error('Failed to copy: ', err);
                        button.innerHTML = '<i class="fas fa-times"></i> Failed';
                        setTimeout(() => {
                            button.innerHTML = '<i class="fas fa-copy"></i> Copy';
                        }, 2000);
                    });
                }

                document.addEventListener('DOMContentLoaded', () => {
                    const detailsWrappers = document.querySelectorAll('.details-wrapper');
                    detailsWrappers.forEach(wrapper => {
                        wrapper.addEventListener('click', () => {
                            wrapper.classList.toggle('active');
                        });
                    });
                });
            </script>
        </body>
        </html>
        """
        if 'home' in app.view_functions:
            home_url = url_for('home')
        else:
            # Fallback to the root URL if no 'home' endpoint exists.
            home_url = '/'
        # ==================================================================
        try:
            # Try package-relative path first
            import mbkauthepy
            package_dir = Path(mbkauthepy.__file__).parent
            template_path = package_dir / 'templates' / 'loginmbkauthe.handlebars'
        except ImportError:
            # Fallback to absolute path (development)
            pass
        from flask import render_template_string


        response = error.get_response()
        response.data = render_template_string(
            template,
            code=error.code,
            name=error.name,
            message=error.description,
            page_url=home_url,  # Use the safely determined URL
            page_name="home"
        )
        response.content_type = "text/html"
        return response

    logger.info("Global HTTP error handler registered.")
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

