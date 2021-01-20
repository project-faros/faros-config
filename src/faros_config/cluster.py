"""Faros Configuration Models - Cluster.

This module contains the configuration models for the cluster section. This
includes configuration of cluster-node specific information.
"""
from pydantic import BaseModel
from typing import List, Optional

from .common import MacAddress, StrEnum


class ManagementProviderItem(StrEnum):
    """The supported management providers."""

    ILO = "ilo"


class ManagementConfig(BaseModel):
    """The config model for the cluster node management."""

    provider: ManagementProviderItem
    user: str
    password: str


class NodeConfig(BaseModel):
    """The config model for cluster nodes themselves."""

    name: str
    mac: MacAddress
    mgmt_mac: MacAddress
    install_drive: Optional[str]


class ClusterConfig(BaseModel):
    """The cluster config section model."""

    pull_secret: str
    management: ManagementConfig
    nodes: List[NodeConfig]
