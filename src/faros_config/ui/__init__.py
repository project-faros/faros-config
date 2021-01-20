"""Faros Configuration User Interface.

The faros_config package provides a mechanism to load, dump, and validate
configuration files in YAML format for the Project Faros Cluster Manager. Also
included is a WSGI application (built in Flask) that serves a Patternfly-based
web form to generate valid configuration files.

This sub-package provides the Flask-based user interface to generate
configuration files, validated through the model.
"""

from .app import app

__all__ = ["app"]
