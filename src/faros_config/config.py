"""Faros Configuration Model.

This module contains the top level configuration model for Project Faros.
"""
import json
from pydantic import BaseModel
from typing import Optional
import yaml

from .bastion import BastionConfig
from .cluster import ClusterConfig
from .common import PydanticEncoder
from .network import NetworkConfig
from .proxy import ProxyConfig


class FarosConfig(BaseModel):
    """Validate, serialize, and deserialize Faros configurations."""

    network: NetworkConfig
    bastion: BastionConfig
    cluster: ClusterConfig
    proxy: Optional[ProxyConfig]

    @classmethod
    def from_yaml(cls, yaml_file: str) -> 'FarosConfig':
        """Instantiate a FarosConfig from a yaml file path."""
        with open(yaml_file) as f:
            config = yaml.safe_load(f)

        return cls.parse_obj(config)

    def to_json(self) -> str:
        """Serialize a FarosConfig object to JSON text."""
        return json.dumps(self, sort_keys=True, indent=4,
                          separators=(',', ': '), cls=PydanticEncoder)
