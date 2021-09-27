#!/usr/bin/env python3
import os
import pytest
from pprint import pprint
from tempfile import mkstemp

from faros_config.inventory import (
    FarosInventory, FarosInventoryConfig, IPAddressManager
)
from faros_config.inventory.cli import main as cli

from .conftest import VALID_CONFIGS, config_data


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


def test_inventory_internals():
    for config_file in VALID_CONFIGS:
        with InventoryTest(config_file) as inv:
            # Make sure that the bastion variables make it to router inventory
            router_group = inv.inv.group('router')
            become_pass = router_group.host('wan')['ansible_become_pass']
            bastion = config_data[config_file]['bastion']
            assert become_pass == bastion['become_pass']

            # Make sure that non-existent groups aren't returned
            assert inv.inv.group('fake_group_name') is None

            # Make sure that adding new hosts drops them into all
            inv.inv.add_host('testhost', hostname='86.7.53.09')
            assert inv.inv.host('testhost')['ansible_host'] == '86.7.53.09'

            # Make sure that adding new hosts in new groups creates them
            inv.inv.add_host('testhost2', group='fake', hostname='86.7.53.09')
            assert inv.inv.group('fake').host('testhost2') is not None

            # Validate static and dynamic pools
            print(f'IPAM Static Pool: {inv.ipam.static_pool}')
            print(f'IPAM Dynamic Pool: {inv.ipam.dynamic_pool}')


if __name__ == '__main__':
    test_inventory_initialization()
    test_inventory_cli()
    test_inventory_internals()
