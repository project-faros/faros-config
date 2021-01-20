"""Faros Configuration Library.

The faros_config package provides a mechanism to load, dump, and validate
configuration files in YAML format for the Project Faros Cluster Manager. Also
included is a WSGI application (built in Flask) that serves a Patternfly-based
web form to generate valid configuration files.

This package serves as the source of truth for how a given Cluster Manager
configuration should be structured and includes supported options for that
version of the Cluster Manager.
"""

from .config import FarosConfig

__all__ = ["FarosConfig"]
