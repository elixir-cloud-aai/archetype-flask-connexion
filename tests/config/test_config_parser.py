"""
Tests for config_parser.py
"""

import pytest

from pydantic import ValidationError

from foca.config.config_parser import ConfigParser
from foca.models.config import Config


TEST_FILE = "tests/test_files/conf_valid.yaml"
TEST_FILE_INVALID = "tests/test_files/conf_invalid_log_level.yaml"
TEST_DICT = {}
TEST_CONFIG_INSTACE = Config()


def test_config_parser_valid_config_file():
    """Test valid YAML parsing"""
    conf = ConfigParser(TEST_FILE)
    assert type(conf.config.dict()) == type(TEST_DICT)
    assert type(conf.config) == type(TEST_CONFIG_INSTACE)


def test_config_parser_invalid_config_file():
    """Test valid YAML parsing"""
    with pytest.raises(ValidationError):
        conf = ConfigParser(TEST_FILE_INVALID)
        assert conf is not None


def test_config_parser_invalid_file_path():
    """Test yaml class, passing invalid YAML file path"""
    conf = ConfigParser(TEST_FILE)
    with pytest.raises(OSError):
        assert conf.parse_yaml("") is not None
