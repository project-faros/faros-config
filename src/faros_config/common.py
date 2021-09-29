"""Faros Configuration - Common classes and variables.

This module contains common utility classes used throughout faros_config.
"""
import json
import ipaddress
from enum import Enum
from pydantic import constr, BaseModel

HostName = constr(regex=r'^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$')
MacAddress = constr(regex=r'(([0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2})|(([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})')  # noqa: E501


class StrEnum(str, Enum):
    """Represent a choice between a fixed set of strings.

    A mix-in of string and enum, representing itself as the string value.
    """

    @classmethod
    def list(cls) -> list:
        """Return a list of the available options in the Enum."""
        return [e.value for e in cls]

    def __str__(self) -> str:
        return self.value


class FarosBaseModel(BaseModel):
    """Faros Base Model for configuration classes."""

    class Config:
        """Configuration class for Pydantic models."""

        allow_population_by_field_name = True


class PydanticEncoder(json.JSONEncoder):
    """Serialize Pydantic models.

    A JSONEncoder subclass that prepares Pydantic models for serialization.
    """

    def default(self, obj):
        """Encode model objects based on their type."""
        if isinstance(obj, BaseModel) and callable(obj.dict):
            return obj.dict(exclude_none=True)
        elif isinstance(obj, ipaddress._IPAddressBase):
            return str(obj)
        else:  # pragma: nocover
            return json.JSONEncoder.default(self, obj)
