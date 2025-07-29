from __future__ import annotations

from pathlib import Path

import pytest

from kelvin.config.appyaml import AppYaml
from kelvin.config.common import AppTypes, ConfigError
from kelvin.config.exporter import ExporterConfig
from kelvin.config.external import ExternalConfig
from kelvin.config.importer import ImporterConfig
from kelvin.config.parser import AppConfigObj, parse_config_file
from kelvin.config.smart_app import SmartAppConfig

CONFIG_DIR = "configs"


def test_parse_exporter_config():
    file_path = Path(__file__).parent / CONFIG_DIR / "exporter.yaml"
    config = parse_config_file(file_path)

    assert isinstance(config, AppConfigObj)
    assert config.type == AppTypes.exporter
    assert isinstance(config.config, ExporterConfig)
    assert config.name == "exporter-x"
    assert config.version == "1.0.0"


def test_parse_importer_config():
    file_path = Path(__file__).parent / CONFIG_DIR / "importer.yaml"
    config = parse_config_file(file_path)

    assert isinstance(config, AppConfigObj)
    assert config.type == AppTypes.importer
    assert isinstance(config.config, ImporterConfig)
    assert config.name == "importer-x"
    assert config.version == "1.0.1"


def test_parse_smartapp_config():
    file_path = Path(__file__).parent / CONFIG_DIR / "smartapp.yaml"
    config = parse_config_file(file_path)

    assert isinstance(config, AppConfigObj)
    assert config.type == AppTypes.app
    assert isinstance(config.config, SmartAppConfig)
    assert config.name == "smart-app-x"
    assert config.version == "1.0.2"


def test_parse_external_config():
    file_path = Path(__file__).parent / CONFIG_DIR / "docker.yaml"
    config = parse_config_file(file_path)

    assert isinstance(config, AppConfigObj)
    assert config.type == AppTypes.docker
    assert isinstance(config.config, ExternalConfig)
    assert config.name == "influxdb"
    assert config.version == "1.0.0"


def test_parse_legacy_docker_config():
    file_path = Path(__file__).parent / CONFIG_DIR / "legacy_docker.yaml"
    config = parse_config_file(file_path)

    assert isinstance(config, AppConfigObj)
    assert config.type == AppTypes.legacy_docker
    assert isinstance(config.config, AppYaml)
    assert config.name == "test-docker-app"
    assert config.version == "1.0.0"
    assert config.is_legacy() is True


def test_with_json():
    file_path = Path(__file__).parent / CONFIG_DIR / "exporter.json"
    config = parse_config_file(file_path)

    assert isinstance(config, AppConfigObj)
    assert config.type == AppTypes.exporter
    assert isinstance(config.config, ExporterConfig)
    assert config.name == "exporter-x"
    assert config.version == "1.0.0"


def test_invalid_yaml():
    file_path = Path(__file__).parent / CONFIG_DIR / "invalid.yaml"
    with pytest.raises(ConfigError):
        parse_config_file(file_path)


def test_missing_file():
    file_path = Path(__file__).parent / CONFIG_DIR / "nonexistent.yaml"
    with pytest.raises(ConfigError):
        parse_config_file(file_path)
