"""Faros Configuration Tests - Configuration."""

import os
import yaml

# Path to the examples to include
example_dir = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '../examples'
))

# A list of paths to working configuration examples
VALID_CONFIGS = [
    f'{example_dir}/example_config.yml',
    f'{example_dir}/example_config_with_install_drives.yml',
    f'{example_dir}/example_config_with_classless_lan.yml'
]
# A list of paths to invalid configuration examples
INVALID_CONFIGS = [
    f'{example_dir}/invalid-no_dhcp.yml',
    f'{example_dir}/invalid-too_few_nodes.yml',
    f'{example_dir}/invalid-bad_hostname.yml'
]

# The raw dictionary objects loaded from the configurations.
config_data = {filename: yaml.safe_load(open(filename))
               for filename in VALID_CONFIGS + INVALID_CONFIGS}
