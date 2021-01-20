"""Faros Configuration Models - Network.

This module contains the configuration models for the network section.
"""
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from pydantic import BaseModel
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

    name: str
    mac: MacAddress


class NameMacIpSet(BaseModel):
    """The config model for a name, MAC address, and IP address type."""

    name: str
    mac: MacAddress
    ip: Union[IPv4Address, IPv6Address]


class DhcpConfig(BaseModel):
    """The config model for the DHCP server configuration."""

    ignore_macs: List[NameMacPair]
    extra_reservations: List[NameMacIpSet]


class LanConfig(BaseModel):
    """The config model for the Faros LAN."""

    subnet: Union[IPv4Network, IPv6Network]
    interfaces: List[str]
    dns_forward_resolvers: Optional[List[Union[IPv4Address, IPv6Address]]]
    dhcp: DhcpConfig


class NetworkConfig(BaseModel):
    """The network section config model."""

    port_forward: List[PortForwardConfigItem]
    lan: LanConfig
