import os
import yaml

example_dir = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '../examples'
))

VALID_CONFIGS = [
    f'{example_dir}/example_config.yml',
    f'{example_dir}/example_config_with_install_drives.yml',
    f'{example_dir}/example_config_with_classless_lan.yml'
]
INVALID_CONFIGS = [f'{example_dir}/invalid-1.yml']

config_data = {filename: yaml.safe_load(open(filename))
               for filename in VALID_CONFIGS + INVALID_CONFIGS}
