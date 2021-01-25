"""Faros Configuration Inventory - CLI.

This module contains the CLI elements necessary to provide an entrypoint to
generate Ansible-format JSON inventories from the configuration.
"""

import argparse
import sys

from faros_config.inventory import (
    FarosInventory, FarosInventoryConfig, IPAddressManager
)


def parse_args(argv: list = []):
    """Parse CLI args for the inventory entrypoint."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--host', action='store')
    parser.add_argument('--reservations-file', action='store',
                        default='/data/ip_addresses')
    parser.add_argument('--ssh-private-key', action='store',
                        default='/data/id_rsa')
    parser.add_argument('--config-file', action='store',
                        default='/data/config.yml')
    args = parser.parse_args(argv)
    return args


def main(argv: list = sys.argv[1:]):
    """Provide the entrypoint for the CLI."""
    # PARSE ARGUMENTS
    args = parse_args(argv)
    if args.list:
        mode = 0
    elif args.verify:
        mode = 2
    else:
        mode = 1

    # INTIALIZE CONFIG
    config = FarosInventoryConfig(args.config_file)

    # INTIALIZE IPAM
    ipam = IPAddressManager(
        args.reservations_file,
        config.network.lan.subnet
    )

    # INITIALIZE INVENTORY
    inv = FarosInventory(mode, args.host)

    # CREATE INVENTORY
    try:
        inv.build(config, ipam, args.ssh_private_key)
        if mode == 0:
            print(inv.to_json())

    except Exception as e:  # pragma: nocover
        if mode == 2:
            sys.stderr.write(config.error)
            sys.stderr.flush()
            sys.exit(1)
        raise(e)

    # DONE
    ipam.save()
