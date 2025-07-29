from __future__ import annotations

from pathlib import Path

import pytest

from kelvin.config.common import AppTypes, ConfigError
from kelvin.config.external import (
    DeploymentDefaults,
    ExternalConfig,
    ExternalFlags,
    SchemasConfig,
)


def test_convert_external_to_manifest():
    """Test successful conversion of ExternalConfig to AppManifest"""
    config = ExternalConfig(
        type="docker",
        name="test-external-app",
        title="Test External App",
        description="An external app",
        version="1.0.0",
        category="optimizer",
        flags=ExternalFlags(),
        ui_schemas=SchemasConfig(configuration="schemas/configuration.json"),
        defaults=DeploymentDefaults(
            system={"env": "production"},
            configuration={"key": "value"},
        ),
    )

    manifest = config.to_manifest(read_schemas=True, workdir=Path(__file__).parent)

    # Check basic properties
    assert manifest.name == "test-external-app"
    assert manifest.title == "Test External App"
    assert manifest.description == "An external app"
    assert manifest.type == AppTypes.docker
    assert manifest.version == "1.0.0"
    assert manifest.category == "optimizer"

    # Check parameters
    assert len(manifest.parameters) == 0

    # Check flags
    assert manifest.flags.spec_version == "5.0.0"

    # Check io
    assert len(manifest.io) == 0

    # Check schemas
    assert manifest.schemas.configuration == {"configuration_schema": {"test1": "string"}}

    # Check defaults
    assert manifest.defaults.app.configuration == {"key": "value"}
    assert manifest.defaults.system == {"env": "production"}


def test_convert_external_to_manifest_no_schemas():
    """Test successful conversion of ExternalConfig to AppManifest without reading schemas"""
    config = ExternalConfig(
        type="docker",
        name="test-external-app",
        title="Test External App",
        description="An external app",
        version="1.0.0",
        flags=ExternalFlags(),
        defaults=DeploymentDefaults(
            system={"env": "production"},
            configuration={"key": "value"},
        ),
    )

    config.to_manifest(read_schemas=False)
    config.to_manifest(read_schemas=True, workdir=Path(__file__).parent)


def test_convert_external_schema_not_found():
    """Test failure to convert ExternalConfig to AppManifest with missing schema file"""
    config = ExternalConfig(
        type="docker",
        name="test-external-app",
        title="Test External App",
        description="An external app",
        version="1.0.0",
        flags=ExternalFlags(),
        ui_schemas=SchemasConfig(configuration="not-found.json"),
        defaults=DeploymentDefaults(
            system={"env": "production"},
            configuration={"key": "value"},
        ),
    )

    config.to_manifest(read_schemas=False)

    with pytest.raises(ConfigError, match="Schema file not-found.json does not exist."):
        config.to_manifest(read_schemas=True)
