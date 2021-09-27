"""Faros Configuration Library.

The faros_config package provides a mechanism to load, dump, and validate
configuration files in YAML format for the Project Faros Cluster Manager.

This package serves as the source of truth for how a given Cluster Manager
configuration should be structured and includes supported options for that
version of the Cluster Manager.
"""

from .config import FarosConfig
from .common import PydanticEncoder

__all__ = ["FarosConfig", "PydanticEncoder"]
