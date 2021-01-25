#!/usr/bin/env python
import pytest
from pprint import pprint
from pydantic import ValidationError

from faros_config import FarosConfig
from .conftest import VALID_CONFIGS, INVALID_CONFIGS


def test_valid_config():
    """Tests loading and dumping a valid config."""
    for configfile in VALID_CONFIGS:
        config = FarosConfig.from_yaml(configfile)
        config_json = config.to_json()
        pprint(config)
        pprint(config_json)


def test_invalid_config():
    """Tests loading invalid configurations."""
    for configfile in INVALID_CONFIGS:
        with pytest.raises(ValidationError):
            _ = FarosConfig.from_yaml(configfile)


if __name__ == '__main__':
    test_valid_config()
