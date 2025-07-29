from __future__ import annotations

from pathlib import Path

import pytest

from kelvin.config.common import ConfigError, CustomActionDef, CustomActionsIO
from kelvin.config.exporter import (
    DeploymentDefaults,
    ExporterConfig,
    ExporterFlags,
    ExporterIO,
    RuntimeUpdateConfig,
    SchemasConfig,
)
from kelvin.config.manifest import DynamicIoOwnership, DynamicIoType


def test_convert_exporter_to_manifest_success():
    """
    Test successful conversion of exporterConfig to AppManifest.
    """
    # Define exporterConfig instance
    exporter_config = ExporterConfig(
        name="test-exporter",
        title="Test Exporter",
        description="This is a test exporter config.",
        type="exporter",
        version="1.0.0",
        category="databricks",
        flags=ExporterFlags(enable_runtime_update=RuntimeUpdateConfig(configuration=False)),
        exporter_io=[
            ExporterIO(name="test_io", data_types=["string"]),
            ExporterIO(name="test_io_cc", data_types=["number"]),
        ],
        ui_schemas=SchemasConfig(
            configuration="schemas/configuration.json",
            io_configuration={"test_io": "schemas/test_io_schema.json", "test_io_cc": "schemas/test_io_cc_schema.json"},
        ),
        defaults=DeploymentDefaults(system={"env": "production"}, configuration={"key": "value"}),
        custom_actions=CustomActionsIO(
            inputs=[CustomActionDef(type="input_action")],
            outputs=[CustomActionDef(type="output_action")],
        ),
    )

    # Convert to AppManifest
    manifest = exporter_config.to_manifest(read_schemas=True, workdir=Path(__file__).parent)

    # Assertions
    assert manifest.name == "test-exporter"
    assert manifest.title == "Test Exporter"
    assert manifest.description == "This is a test exporter config."
    assert manifest.type == "exporter"
    assert manifest.version == "1.0.0"
    assert manifest.category == "databricks"

    # Validate flags
    assert manifest.flags.spec_version == "5.0.0"
    assert manifest.flags.enable_runtime_update.configuration is False
    assert manifest.flags.resources_required is None

    # Validate dynamic IO
    assert len(manifest.dynamic_io) == 2
    dynamic_io = manifest.dynamic_io[0]
    assert dynamic_io.type_name == "test_io"
    assert dynamic_io.data_types == ["string"]
    assert dynamic_io.ownership == DynamicIoOwnership.remote
    assert dynamic_io.type == DynamicIoType.data
    dynamic_io = manifest.dynamic_io[1]
    assert dynamic_io.type_name == "test_io_cc"
    assert dynamic_io.data_types == ["number"]
    assert dynamic_io.ownership == DynamicIoOwnership.remote
    assert dynamic_io.type == DynamicIoType.data

    # Validate schemas
    assert manifest.schemas.configuration == {"configuration_schema": {"test1": "string"}}
    assert len(manifest.schemas.io_configurations) == 2
    assert manifest.schemas.io_configurations[0].type_name == "test_io"
    assert manifest.schemas.io_configurations[0].io_schema == {"test_io_schema": {"test3": "string"}}
    assert manifest.schemas.io_configurations[1].type_name == "test_io_cc"
    assert manifest.schemas.io_configurations[1].io_schema == {"test_io_schema_cc": {"test4": "string"}}
    # Validate defaults
    assert manifest.defaults.app.configuration == {"key": "value"}
    assert manifest.defaults.system == {"env": "production"}

    # Validate custom actions
    assert len(manifest.custom_actions) == 2
    assert manifest.custom_actions[0].type == "input_action"
    assert manifest.custom_actions[0].way == "input-ca"
    assert manifest.custom_actions[1].type == "output_action"
    assert manifest.custom_actions[1].way == "output-ca"


def test_convert_export_to_manifest_missing_schema():
    """
    Test that missing schema file raises an error.
    """
    # Define ImporterConfig instance with a missing schema
    exporter_config = ExporterConfig(
        name="test-exporter",
        title="Test Exporter",
        description="This is a test exporter config.",
        type="exporter",
        version="1.0.0",
        flags=ExporterFlags(enable_runtime_update=RuntimeUpdateConfig(io=True, configuration=False)),
        ui_schemas=SchemasConfig(
            configuration="",
            io_configuration={"test_io": "schemas/missing_config.json"},
        ),
    )

    # Expect an error due to missing schema file
    with pytest.raises(ConfigError, match="Schema file .* does not exist."):
        exporter_config.to_manifest(read_schemas=True, workdir=Path(__file__).parent)
