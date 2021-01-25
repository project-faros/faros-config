"""Faros Configuration Inventory - Inventory.

This module contains the classes that generate the dictionary structure from
a configuration object.
"""

import ipaddress
import json
from collections import defaultdict

from faros_config import PydanticEncoder


class FarosInventoryGroup(object):
    """Structure inventory data according to groups."""

    def __init__(self, parent, name):
        """Map metadata."""
        self._parent = parent
        self._name = name

    def add_group(self, name, **groupvars):
        """Add this group to the parent group."""
        return(self._parent.add_group(name, self._name, **groupvars))

    def add_host(self, name, hostname=None, **hostvars):
        """Add a host to this group."""
        return(self._parent.add_host(name, self._name, hostname, **hostvars))

    def host(self, name):
        """Return the host embedded in the parent from this group."""
        return self._parent.host(name)


class FarosInventory(object):
    """Structure inventory data by groups and hosts.

    Also enables the building of the full nested dictionary object.
    """

    _modes = ['list', 'host', 'verify', 'none']
    _data = {"_meta": {"hostvars": defaultdict(dict)}}

    def __init__(self, mode=0, host=None):
        """Instantiate an inventory with data to prepare it for building."""
        if mode == 1:
            # host info requested
            # current, only list and none are implimented
            raise NotImplementedError()

        self._mode = mode
        self._host = host

    def host(self, name):
        """Return a specific host from this inventory."""
        return self._data['_meta']['hostvars'].get(name)

    def group(self, name):
        """Return a specific group from this inventory."""
        if name in self._data:
            return FarosInventoryGroup(self, name)
        else:
            return None

    def add_group(self, name, parent=None, **groupvars):
        """Add a new group to this inventory."""
        self._data[name] = {'hosts': [], 'vars': groupvars, 'children': []}

        if parent:
            if parent not in self._data:  # pragma: nocover
                self.add_group(parent)
            self._data[parent]['children'].append(name)

        return FarosInventoryGroup(self, name)

    def add_host(self, name, group=None, hostname=None, **hostvars):
        """Add a new host to this inventory."""
        if not group:
            group = 'all'
        if group not in self._data:
            self.add_group(group)

        if hostname:
            hostvars.update({'ansible_host': hostname})

        self._data[group]['hosts'].append(name)
        self._data['_meta']['hostvars'][name].update(hostvars)

    def to_json(self):
        """Return this inventory as completely serialized JSON."""
        return json.dumps(self._data, sort_keys=True, indent=4,
                          separators=(',', ': '), cls=PydanticEncoder)

    def build(self, config, ipam, key):
        """Build this inventory's structure out after population."""
        # GATHER INFORMATION FOR EXTRA NODES
        for node in config.network.lan.dhcp.extra_reservations:
            addr = ipam.get(node.mac, str(node.ip))
            node.ip = ipaddress.IPv4Address(addr)

        # CREATE INVENTORY
        self.add_group(
            'all', None,
            ansible_ssh_private_key_file=key,
            cluster_name=config.shim_vars['CLUSTER_NAME'],
            cluster_domain=config.shim_vars['CLUSTER_DOMAIN'],
            admin_password=config.bastion.become_pass,
            pull_secret=json.loads(config.cluster.pull_secret),
            mgmt_provider=config.cluster.management.provider,
            mgmt_user=config.cluster.management.user,
            mgmt_password=config.cluster.management.password,
            install_disk=config.shim_vars['BOOT_DRIVE'],
            loadbalancer_vip=ipam['loadbalancer'],
            dynamic_ip_range=ipam.dynamic_pool,
            reverse_ptr_zone=ipam.reverse_ptr_zone,
            subnet=str(config.network.lan.subnet.network_address),
            subnet_mask=config.network.lan.subnet.prefixlen,
            wan_ip=config.shim_vars['BASTION_IP_ADDR'],
            extra_nodes=config.network.lan.dhcp.extra_reservations,
            ignored_macs=config.network.lan.dhcp.ignore_macs,
            dns_forwarders=config.network.lan.dns_forward_resolvers,
            proxy=config.proxy is not None,
            proxy_http=config.proxy.http if config.proxy is not None else '',
            proxy_https=config.proxy.https if config.proxy is not None else '',
            proxy_noproxy=config.proxy.noproxy if config.proxy is not None else [],  # noqa: E501
            proxy_ca=config.proxy.ca if config.proxy is not None else ''
        )

        infra = self.add_group('infra')
        router = infra.add_group(
            'router',
            wan_interface=config.shim_vars['WAN_INT'],
            lan_interfaces=config.network.lan.interfaces,
            all_interfaces=config.shim_vars['BASTION_INTERFACES'].split(),
            allowed_services=config.network.port_forward
        )
        # ROUTER INTERFACES
        router.add_host(
            'wan', config.shim_vars['BASTION_IP_ADDR'],
            ansible_become_pass=config.bastion.become_pass,
            ansible_ssh_user=config.shim_vars['BASTION_SSH_USER']
        )
        router.add_host(
            'lan',
            ipam['bastion'],
            ansible_become_pass=config.bastion.become_pass,
            ansible_ssh_user=config.shim_vars['BASTION_SSH_USER']
        )
        # DNS NODE
        router.add_host(
            'dns',
            ipam['bastion'],
            ansible_become_pass=config.bastion.become_pass,
            ansible_ssh_user=config.shim_vars['BASTION_SSH_USER']
        )
        # DHCP NODE
        router.add_host(
            'dhcp',
            ipam['bastion'],
            ansible_become_pass=config.bastion.become_pass,
            ansible_ssh_user=config.shim_vars['BASTION_SSH_USER']
        )
        # LOAD BALANCER NODE
        router.add_host(
            'loadbalancer',
            ipam['loadbalancer'],
            ansible_become_pass=config.bastion.become_pass,
            ansible_ssh_user=config.shim_vars['BASTION_SSH_USER']
        )

        # BASTION NODE
        bastion = infra.add_group('bastion_hosts')
        bastion.add_host(
            config.shim_vars['BASTION_HOST_NAME'],
            ipam['bastion'],
            ansible_become_pass=config.bastion.become_pass,
            ansible_ssh_user=config.shim_vars['BASTION_SSH_USER']
        )

        # CLUSTER NODES
        cluster = self.add_group('cluster')
        # BOOTSTRAP NODE
        ip = ipam['bootstrap']
        cluster.add_host(
            'bootstrap', ip,
            ansible_ssh_user='core',
            node_role='bootstrap'
        )
        # CLUSTER CONTROL PLANE NODES
        cp = cluster.add_group('control_plane', node_role='master')
        for count, node in enumerate(config.cluster.nodes):
            ip = ipam[node.mac]
            mgmt_ip = ipam[node.mgmt_mac]
            cp.add_host(
                node.name, ip,
                mac_address=node.mac,
                mgmt_mac_address=node.mgmt_mac,
                mgmt_hostname=mgmt_ip,
                ansible_ssh_user='core',
                cp_node_id=count
            )
            if node.install_drive is not None:
                cp.host(node.name)['install_disk'] = node.install_drive

        # VIRTUAL NODES
        virt = self.add_group(
            'virtual',
            mgmt_provider='kvm',
            mgmt_hostname='bastion',
            install_disk='vda'
        )
        virt.add_host('bootstrap')

        # MGMT INTERFACES
        mgmt = self.add_group(
            'management',
            ansible_ssh_user=config.cluster.management.user,
            ansible_ssh_pass=config.cluster.management.password
        )
        for node in config.cluster.nodes:
            mgmt.add_host(
                node.name + '-mgmt', ipam[node.mgmt_mac],
                mac_address=node.mgmt_mac
            )
