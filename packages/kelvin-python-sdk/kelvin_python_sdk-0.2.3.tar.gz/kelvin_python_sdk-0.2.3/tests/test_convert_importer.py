from __future__ import annotations

from pathlib import Path

import pytest

from kelvin.config.common import ConfigError, CustomActionDef, CustomActionsIO
from kelvin.config.importer import (
    DeploymentDefaults,
    ImporterConfig,
    ImporterFlags,
    ImporterIO,
    RuntimeUpdateConfig,
    SchemasConfig,
)
from kelvin.config.manifest import DynamicIoOwnership, DynamicIoType


def test_convert_importer_to_manifest_success():
    """
    Test successful conversion of ImporterConfig to AppManifest.
    """
    # Define ImporterConfig instance
    importer_config = ImporterConfig(
        name="test-importer",
        title="Test Importer",
        description="This is a test importer config.",
        type="importer",
        version="1.0.0",
        category="azure",
        flags=ImporterFlags(enable_runtime_update=RuntimeUpdateConfig(configuration=False), resources_required=True),
        importer_io=[
            ImporterIO(name="test_io", data_types=["string"], control=False),
            ImporterIO(name="test_io_cc", data_types=["number"], control=True),
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
    manifest = importer_config.to_manifest(read_schemas=True, workdir=Path(__file__).parent)

    # Assertions
    assert manifest.name == "test-importer"
    assert manifest.title == "Test Importer"
    assert manifest.description == "This is a test importer config."
    assert manifest.type == "importer"
    assert manifest.version == "1.0.0"
    assert manifest.category == "azure"

    # Validate flags
    assert manifest.flags.spec_version == "5.0.0"
    assert manifest.flags.enable_runtime_update.configuration is False
    assert manifest.flags.resources_required is True

    # Validate dynamic IO
    assert len(manifest.dynamic_io) == 2
    dynamic_io = manifest.dynamic_io[0]
    assert dynamic_io.type_name == "test_io"
    assert dynamic_io.data_types == ["string"]
    assert dynamic_io.ownership == DynamicIoOwnership.owned
    assert dynamic_io.type == DynamicIoType.data
    dynamic_io = manifest.dynamic_io[1]
    assert dynamic_io.type_name == "test_io_cc"
    assert dynamic_io.data_types == ["number"]
    assert dynamic_io.ownership == DynamicIoOwnership.owned
    assert dynamic_io.type == DynamicIoType.both

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


def test_convert_importer_to_manifest_missing_schema():
    """
    Test that missing schema file raises an error.
    """
    # Define ImporterConfig instance with a missing schema
    importer_config = ImporterConfig(
        name="test-importer",
        title="Test Importer",
        description="This is a test importer config.",
        type="importer",
        version="1.0.0",
        flags=ImporterFlags(enable_runtime_update=RuntimeUpdateConfig(io=True, configuration=False)),
        ui_schemas=SchemasConfig(configuration="schemas/missing_config.json", io_configuration={}),
    )

    # Expect an error due to missing schema file
    with pytest.raises(ConfigError, match="Schema file .* does not exist."):
        importer_config.to_manifest(read_schemas=True, workdir=Path(__file__).parent)
