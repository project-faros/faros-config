"""Faros Configuration Models - Proxy.

This module contains the configuration models for the proxy section.
"""
from pydantic import BaseModel
from typing import List


class ProxyConfig(BaseModel):
    """The proxy config section model."""

    http: str
    https: str
    noproxy: List[str]
    ca: str
