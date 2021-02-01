"""Faros Configuration Models - Network.

This module contains the configuration models for the network section.
"""
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from pydantic import BaseModel, Field
from typing import List, Optional, Union

from .common import MacAddress, StrEnum


class PortForwardConfigItem(StrEnum):
    """The supported port-forwarding applications."""

    SSH_TO_BASTION = "SSH to Bastion"
    HTTPS_TO_CLUSTER_API = "HTTPS to Cluster API"
    HTTP_TO_CLUSTER_APPS = "HTTP to Cluster Apps"
    HTTPS_TO_CLUSTER_APPS = "HTTPS to Cluster Apps"
    HTTPS_TO_COCKPIT_PANEL = "HTTPS to Cockpit Panel"


class NameMacPair(BaseModel):
    """The config model for a basic pairing of name and MAC address."""

    name: str = Field(
        description="A friendly name for the MAC you'd like ignored."
    )
    mac: MacAddress = Field(
        description="The MAC address you'd like ignored."
    )


class NameMacIpSet(BaseModel):
    """The config model for a name, MAC address, and IP address type."""

    name: str = Field(
        description="A friendly name for the IP address reservation."
    )
    mac: MacAddress = Field(
        description="The MAC address you'd like to have a reserved IP for."
    )
    ip: Union[IPv4Address, IPv6Address] = Field(
        description="The IP address you'd like assigned for the MAC address."
    )


class DhcpConfig(BaseModel):
    """Configuration of the DHCP server on the bastion."""

    ignore_macs: Optional[List[NameMacPair]] = Field(
        list(),
        description="The list of MAC addresses to ignore."
    )
    extra_reservations: Optional[List[NameMacIpSet]] = Field(
        list(),
        description="The list of extra DHCP static reservations."
    )


class LanConfig(BaseModel):
    """Configuration of the Faros LAN."""

    subnet: Union[IPv4Network, IPv6Network] = Field(
        description="The CIDR notation for the subnet to use for the LAN."
    )
    interfaces: List[str] = Field(
        description=("The name of the interfaces on the bastion to place on "
                     "the Faros LAN bridge.")
    )
    dns_forward_resolvers: Optional[List[Union[IPv4Address, IPv6Address]]] = Field(  # noqa: E501
        list(),
        description="A list of upstream DNS servers to resolve queries from."
    )
    dhcp: DhcpConfig = Field(
        description="Configuration of the DHCP server on the bastion."
    )


class NetworkConfig(BaseModel):
    """Networking configuration on the bastion."""

    port_forward: List[PortForwardConfigItem] = Field(
        [PortForwardConfigItem("SSH to Bastion")],
        description=("A list of services to forward to the cluster from the "
                     "WAN network, exposing them outside the cluster.")
    )
    lan: LanConfig = Field(
        description="Configuration of the Faros LAN."
    )
