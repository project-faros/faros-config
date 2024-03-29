"""Faros Configuration Inventory.

The faros_config package provides a mechanism to load, dump, and validate
configuration files in YAML format for the Project Faros Cluster Manager.

This sub-package provides the Inventory classes and cli for generating Ansible
inventory in the expected JSON format from configuration primatives.
"""

from .inventory import FarosInventory
from .config import FarosInventoryConfig
from .ipam import IPAddressManager

__all__ = [
    'FarosInventory',
    'FarosInventoryConfig',
    'IPAddressManager'
]
