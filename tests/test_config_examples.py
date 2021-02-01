#!/usr/bin/env python
"""Faros Configuration Tests - Example Validation."""

import pytest
from pprint import pprint
from pydantic import ValidationError

from faros_config import FarosConfig
from .conftest import VALID_CONFIGS, INVALID_CONFIGS


def test_valid_config():
    """Test loading and dumping a valid config."""
    for configfile in VALID_CONFIGS:
        print(configfile)
        config = FarosConfig.from_yaml(configfile)
        config_json = config.to_json()
        pprint(config)
        pprint(config_json)


def test_invalid_config():
    """Test loading invalid configurations."""
    for configfile in INVALID_CONFIGS:
        with pytest.raises(ValidationError):
            _ = FarosConfig.from_yaml(configfile)


if __name__ == '__main__':
    """Call tests when invoked directly."""
    test_valid_config()
    test_invalid_config()
