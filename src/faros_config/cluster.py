"""Faros Configuration Models - Cluster.

This module contains the configuration models for the cluster section. This
includes configuration of cluster-node specific information.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional

from .common import HostName, MacAddress, StrEnum


class ManagementProviderItem(StrEnum):
    """The supported management providers."""

    ILO = "ilo"


class ManagementConfig(BaseModel):
    """Configuration for management of bare metal nodes."""

    provider: ManagementProviderItem = Field(
        ManagementProviderItem("ilo"),
        description="The management provider for this cluster."
    )
    user: str = Field(
        description="The username for the management provider."
    )
    password: str = Field(
        description="The password for the management provider."
    )


class NodeConfig(BaseModel):
    """Configuration for Faros cluster nodes."""

    name: HostName = Field(
        description="A DNS-compliant friendly name for the node."
    )
    mac: MacAddress = Field(
        description=("The MAC address of the node that should be used for PXE "
                     "and cluster networking.")
    )
    mgmt_mac: MacAddress = Field(
        description="The MAC address of the management interface for the node."
    )
    install_drive: Optional[str] = Field(
        description="The device path for the drive to install CoreOS onto."
    )


class ClusterConfig(BaseModel):
    """The cluster config section model."""

    pull_secret: str = Field(
        description=("The Red Hat pull secret for OpenShift installation, "
                     "acquired from https://cloud.redhat.com.")
    )
    management: ManagementConfig = Field(
        description="Configuration for management of bare metal nodes."
    )
    nodes: List[NodeConfig] = Field(
        description="Configuration for Faros cluster nodes."
    )

    @validator('nodes')
    def exactly_three_nodes(cls, v):
        """Confirm that we are building a cluster of three nodes."""
        if len(v) != 3:
            raise ValueError('must have exactly three nodes')
        return v
