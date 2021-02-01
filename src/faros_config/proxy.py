"""Faros Configuration Models - Proxy.

This module contains the configuration models for the proxy section.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ProxyConfig(BaseModel):
    """Configuration of the HTTP/S proxy for the cluster."""

    http: Optional[str] = Field(
        description="The HTTP proxy endpoint"
    )
    https: Optional[str] = Field(
        description="The HTTPS proxy endpoint"
    )
    noproxy: Optional[List[str]] = Field(
        [],
        description="The list of sites that shouldn't be proxied."
    )
    ca: Optional[str] = Field(
        description="The HTTPS proxy endpoint's certificate authority."
    )
