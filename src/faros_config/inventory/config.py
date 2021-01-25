"""Faros Configuration Inventory - Config.

This module contains the wrapper around the base FarosConfig object to provide
the Ansible inventory access to variables from the cluster-manager environment.
"""

import os

from faros_config import FarosConfig


class FarosInventoryConfig(object):
    """Wrap a FarosConfig object with Environment variable context."""

    shim_var_keys = [
        'WAN_INT',
        'BASTION_IP_ADDR',
        'BASTION_INTERFACES',
        'BASTION_HOST_NAME',
        'BASTION_SSH_USER',
        'CLUSTER_DOMAIN',
        'CLUSTER_NAME',
        'BOOT_DRIVE',
    ]

    def __init__(self, yaml_file):
        """Build the configuration.

        Maps relevant environment variables into the shim_vars property.
        """
        self.shim_vars = {}
        for var in self.shim_var_keys:
            self.shim_vars[var] = os.getenv(var)
        config = FarosConfig.from_yaml(yaml_file)
        self.network = config.network
        self.bastion = config.bastion
        self.cluster = config.cluster
        self.proxy = config.proxy
