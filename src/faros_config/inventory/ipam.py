"""Faros Configuration Inventory - IPAM.

This module contains the class for managing IP address assignments within the
config-provided pool.
"""

import pickle  # nosec


class IPAddressManager(dict):
    """Track IP address asignments within a subnet.

    Saves the allocated IP address assignments into a pickle file so it can
    be reinstantiated across runs with the same data and metadata.
    """

    def __init__(self, save_file, subnet):
        """Initialize the IPAM."""
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
            restore = pickle.load(open(save_file, 'rb'))  # nosec
        except:  # noqa: E722
            restore = {}
        self.update(restore)

        # reserve the first ip for the bastion
        _ = self['bastion']

    def __getitem__(self, key):
        """Retrieve the IP address reservation for an item.

        If it has already been allocated, return it. It not, allocate it and
        record the assignment first before returning it.
        """
        key = key.lower()
        try:
            return super().__getitem__(key)
        except KeyError:
            new_ip = self._next_ip()
            self[key] = new_ip
            return new_ip

    def __setitem__(self, key, value):
        """Set an IP address reservation manually."""
        return super().__setitem__(key.lower(), value)

    def _next_ip(self):
        """Return the next IP in a subnet."""
        used_ips = list(self.values())
        loop = True

        while loop:
            new_ip = next(self._generator).exploded
            loop = new_ip in used_ips
        return new_ip

    def get(self, key, value=None):
        """Return an IP address, optionally setting it if unassigned."""
        if value and value not in self.values():
            self[key] = value
        return self[key]

    def save(self):
        """Save IP address assignments in a pickle."""
        with open(self._save_file, 'wb') as handle:
            pickle.dump(dict(self), handle)  # nosec

    @property
    def static_pool(self):
        """Represent the pool for static assignments."""
        return str(self._static_pool)

    @property
    def dynamic_pool(self):
        """Represent the pool for dynamic assignments."""
        return str(self._dynamic_pool)

    @property
    def reverse_ptr_zone(self):
        """Represent the PTR zone definition."""
        return str(self._reverse_ptr_zone)
