import os

example_dir = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '../examples'
))

VALID_CONFIGS = [f'{example_dir}/example_config.yml']
INVALID_CONFIGS = [f'{example_dir}/invalid-1.yml']
