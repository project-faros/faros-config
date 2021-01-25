#!/usr/bin/env python3
import os
import pytest
from pprint import pprint
from tempfile import mkstemp

from faros_config.inventory import (
    FarosInventory, FarosInventoryConfig, IPAddressManager
)
from faros_config.inventory.cli import main as cli

from .conftest import VALID_CONFIGS


class InventoryTest(object):
    def __init__(self, config_path):
        self.config_path = config_path

    def __enter__(self):
        print('in context')
        self.config = FarosInventoryConfig(self.config_path)
        self.ipam_file = mkstemp()[1]
        self.ssh_private_key = mkstemp()[1]
        self.ipam = IPAddressManager(self.ipam_file,
                                     self.config.network.lan.subnet)
        self.inv = FarosInventory(0, [])
        self.inv.build(self.config, self.ipam, self.ssh_private_key)
        self.json = self.inv.to_json()
        return self

    def __exit__(self, *exc):
        os.remove(self.ipam_file)
        os.remove(self.ssh_private_key)


def test_inventory_initialization():
    for config_file in VALID_CONFIGS:
        with InventoryTest(config_file) as inv:
            pprint(inv.json)


def test_inventory_cli():
    for config_file in VALID_CONFIGS:
        ipam_file = mkstemp()[1]
        ssh_private_key = mkstemp()[1]
        # Do them all twice to ensure we can load an existing IPAM
        for i in range(2):
            cli([
                '--list',
                '--reservations-file', ipam_file,
                '--ssh-private-key', ssh_private_key,
                '--config-file', config_file
            ])
        cli([
            '--verify',
            '--reservations-file', ipam_file,
            '--ssh-private-key', ssh_private_key,
            '--config-file', config_file
        ])
        with pytest.raises(NotImplementedError):
            cli([
                '--host', 'virtual',
                '--reservations-file', ipam_file,
                '--ssh-private-key', ssh_private_key,
                '--config-file', config_file
            ])
        os.remove(ipam_file)
        os.remove(ssh_private_key)


if __name__ == '__main__':
    test_inventory_initialization()
    test_inventory_cli()
