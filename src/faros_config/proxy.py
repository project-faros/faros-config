"""Faros Configuration Models - Proxy.

This module contains the configuration models for the proxy section.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ProxyConfig(BaseModel):
    """Configuration of the HTTP/S proxy for the cluster."""

    http: Optional[str] = Field(
        alias="HTTP Proxy",
        description="The HTTP proxy endpoint"
    )
    https: Optional[str] = Field(
        alias="HTTPS Proxy",
        description="The HTTPS proxy endpoint"
    )
    noproxy: Optional[List[str]] = Field(
        [],
        alias="Proxy-exempt Sites",
        description="The list of sites that shouldn't be proxied."
    )
    ca: Optional[str] = Field(
        alias="HTTPS Proxy CA",
        description="The HTTPS proxy endpoint's certificate authority."
    )

    class Config:
        """Configuration class for Pydantic models."""

        allow_population_by_field_name = True
