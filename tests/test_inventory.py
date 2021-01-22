#!/usr/bin/env python3
from collections import defaultdict
from faros_config import FarosConfig, PydanticEncoder
import ipaddress
import json
import os
import pickle

from .conftest import VALID_CONFIGS


SSH_PRIVATE_KEY = '/data/id_rsa'
IP_RESERVATIONS = '/data/ip_addresses'


class InventoryGroup(object):

    def __init__(self, parent, name):
        self._parent = parent
        self._name = name

    def add_group(self, name, **groupvars):
        return(self._parent.add_group(name, self._name, **groupvars))

    def add_host(self, name, hostname=None, **hostvars):
        return(self._parent.add_host(name, self._name, hostname, **hostvars))

    def host(self, name):
        return self._parent.host(name)


class Inventory(object):

    _modes = ['list', 'host', 'verify', 'none']
    _data = {"_meta": {"hostvars": defaultdict(dict)}}

    def __init__(self, mode=0, host=None):
        if mode == 1:
            # host info requested
            # current, only list and none are implimented
            raise NotImplementedError()

        self._mode = mode
        self._host = host

    def host(self, name):
        return self._data['_meta']['hostvars'].get(name)

    def group(self, name):
        if name in self._data:
            return InventoryGroup(self, name)
        else:
            return None

    def add_group(self, name, parent=None, **groupvars):
        self._data[name] = {'hosts': [], 'vars': groupvars, 'children': []}

        if parent:
            if parent not in self._data:
                self.add_group(parent)
            self._data[parent]['children'].append(name)

        return InventoryGroup(self, name)

    def add_host(self, name, group=None, hostname=None, **hostvars):
        if not group:
            group = 'all'
        if group not in self._data:
            self.add_group(group)

        if hostname:
            hostvars.update({'ansible_host': hostname})

        self._data[group]['hosts'].append(name)
        self._data['_meta']['hostvars'][name].update(hostvars)

    def to_json(self):
        return json.dumps(self._data, sort_keys=True, indent=4,
                          separators=(',', ': '), cls=PydanticEncoder)


class IPAddressManager(dict):

    def __init__(self, save_file, subnet):
        super().__init__()
        self._save_file = save_file

        # parse the subnet definition into a static and dynamic pool
        divided = subnet.subnets()
        self._static_pool = next(divided)
        self._dynamic_pool = next(divided)
        self._generator = self._static_pool.hosts()

        # calculate reverse dns zone
        classful_prefix = [32, 24, 16, 8, 0]
        classful = subnet
        while classful.prefixlen not in classful_prefix:
            classful = classful.supernet()
        host_octets = classful_prefix.index(classful.prefixlen)
        self._reverse_ptr_zone = \
            '.'.join(classful.reverse_pointer.split('.')[host_octets:])

        # load the last saved state
        try:
            restore = pickle.load(open(save_file, 'rb'))
        except:  # noqa: E722
            restore = {}
        self.update(restore)

        # reserve the first ip for the bastion
        _ = self['bastion']

    def __getitem__(self, key):
        key = key.lower()
        try:
            return super().__getitem__(key)
        except KeyError:
            new_ip = self._next_ip()
            self[key] = new_ip
            return new_ip

    def __setitem__(self, key, value):
        return super().__setitem__(key.lower(), value)

    def _next_ip(self):
        used_ips = list(self.values())
        loop = True

        while loop:
            new_ip = next(self._generator).exploded
            loop = new_ip in used_ips
        return new_ip

    def get(self, key, value=None):
        if value and value not in self.values():
            self[key] = value
        return self[key]

    def save(self):
        with open(self._save_file, 'wb') as handle:
            pickle.dump(dict(self), handle)

    @property
    def static_pool(self):
        return str(self._static_pool)

    @property
    def dynamic_pool(self):
        return str(self._dynamic_pool)

    @property
    def reverse_ptr_zone(self):
        return str(self._reverse_ptr_zone)


class Config(object):
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
        self.shim_vars = {}
        for var in self.shim_var_keys:
            self.shim_vars[var] = os.getenv(var)
        config = FarosConfig.from_yaml(yaml_file)
        self.network = config.network
        self.bastion = config.bastion
        self.cluster = config.cluster
        self.proxy = config.proxy


def main(config, ipam, inv):
    # GATHER INFORMATION FOR EXTRA NODES
    for node in config.network.lan.dhcp.extra_reservations:
        addr = ipam.get(node.mac, str(node.ip))
        node.ip = ipaddress.IPv4Address(addr)

    # CREATE INVENTORY
    inv.add_group(
        'all', None,
        ansible_ssh_private_key_file=SSH_PRIVATE_KEY,
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
        proxy_noproxy=config.proxy.noproxy if config.proxy is not None else [],
        proxy_ca=config.proxy.ca if config.proxy is not None else ''
    )

    infra = inv.add_group('infra')
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
    cluster = inv.add_group('cluster')
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
            cp.host(node['name'])['install_disk'] = node.install_drive

    # VIRTUAL NODES
    virt = inv.add_group(
        'virtual',
        mgmt_provider='kvm',
        mgmt_hostname='bastion',
        install_disk='vda'
    )
    virt.add_host('bootstrap')

    # MGMT INTERFACES
    mgmt = inv.add_group(
        'management',
        ansible_ssh_user=config.cluster.management.user,
        ansible_ssh_pass=config.cluster.management.password
    )
    for node in config.cluster.nodes:
        mgmt.add_host(
            node.name + '-mgmt', ipam[node.mgmt_mac],
            mac_address=node.mgmt_mac
        )


def instantiate_inventory(config_path: str = '/data/config.yml'):
    # INTIALIZE CONFIG
    config = Config(config_path)

    # INTIALIZE IPAM
    ipam = IPAddressManager(
        IP_RESERVATIONS,
        config.network.lan.subnet
    )

    # INITIALIZE INVENTORY
    inv = Inventory(0, [])

    # CREATE INVENTORY
    main(config, ipam, inv)
    print(inv.to_json())


def test_inventory_initialization():
    env_var_mapping = {
        'WAN_INT': 'eno2',
        'BASTION_IP_ADDR': '10.1.1.10',
        'BASTION_INTERFACES': 'eno1 eno5 eno3 eno4 enp1s0f4u4',
        'BASTION_HOST_NAME': 'bastion',
        'BASTION_SSH_USER': 'jharmison',
        'CLUSTER_DOMAIN': 'jharmison.com',
        'CLUSTER_NAME': 'kubeframe',
        'BOOT_DRIVE': 'nvme0n1'
    }
    for env_var, env_var_value in env_var_mapping.items():
        os.environ[env_var] = env_var_value

    for config_file in VALID_CONFIGS:
        instantiate_inventory(config_path=config_file)
