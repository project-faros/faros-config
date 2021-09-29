"""Faros Configuration Models - Cluster.

This module contains the configuration models for the cluster section. This
includes configuration of cluster-node specific information.
"""
from pydantic import Field, validator
from typing import List, Optional

from .common import FarosBaseModel, HostName, MacAddress, StrEnum


class ManagementProviderItem(StrEnum):
    """The supported management providers."""

    iLO = "ilo"


class ManagementConfig(FarosBaseModel):
    """Configuration for management of bare metal nodes."""

    provider: ManagementProviderItem = Field(
        ManagementProviderItem("ilo"),
        alias="Management Provider",
        description="The management provider for this cluster."
    )
    user: str = Field(
        alias="Management Username",
        description="The username for the management provider."
    )
    password: str = Field(
        alias="Management Password",
        description="The password for the management provider."
    )


class NodeConfig(FarosBaseModel):
    """Configuration for Faros cluster nodes."""

    name: HostName = Field(
        alias="Node Hostname",
        description="A DNS-compliant friendly name for the node."
    )
    mac: MacAddress = Field(
        alias="Node MAC Address",
        description=("The MAC address of the node that should be used for PXE "
                     "and cluster networking.")
    )
    mgmt_mac: MacAddress = Field(
        alias="Node Management MAC Address",
        description="The MAC address of the management interface for the node."
    )
    install_drive: Optional[str] = Field(
        alias="Node Installation Drive",
        description="The device path for the drive to install CoreOS onto."
    )


class ClusterConfig(FarosBaseModel):
    """The cluster config section model."""

    pull_secret: str = Field(
        alias="Pull Secret",
        description=("The Red Hat pull secret for OpenShift installation, "
                     "acquired from https://cloud.redhat.com.")
    )
    management: ManagementConfig = Field(
        alias="Management Configuration",
        description="Configuration for management of bare metal nodes."
    )
    nodes: List[NodeConfig] = Field(
        alias="Node Configuration",
        description="Configuration for Faros cluster nodes."
    )

    @validator('nodes')
    def exactly_three_nodes(cls, v):
        """Confirm that we are building a cluster of three nodes."""
        if len(v) != 3:
            raise ValueError('must have exactly three nodes')
        return v
