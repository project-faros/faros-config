"""Faros Configuration UI - Application.

This module contains the Flask app for integrating the blueprints.
"""
from flask import (
    Flask,
    redirect,
    url_for,
    send_from_directory
)
import secrets

from .api_bp import api_bp
from .form_bp import form_bp

app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(form_bp, url_prefix='/form')
app.config['SECRET_KEY'] = secrets.token_hex(16)


@app.route('/')
def index():
    """Redirect to the form page by default."""
    return redirect(url_for('config_form.form'))


@app.route('/js/<path:path>')
def send_js(path: str):
    """Send the JavaScript files requested."""
    return send_from_directory('static/js', path)


@app.route('/css/<path:path>')
def send_css(path: str):
    """Send the CSS files requested."""
    return send_from_directory('static/css', path)


@app.route('/fonts/<path:path>')
def send_fonts(path: str):
    """Send the font requested."""
    return send_from_directory('static/fonts', path)
