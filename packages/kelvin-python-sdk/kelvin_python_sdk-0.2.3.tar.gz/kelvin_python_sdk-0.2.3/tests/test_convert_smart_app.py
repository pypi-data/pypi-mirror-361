from __future__ import annotations

from pathlib import Path

import pytest

from kelvin.config.common import AppTypes, ConfigError, CustomActionDef, CustomActionsIO
from kelvin.config.manifest import IOWay
from kelvin.config.smart_app import (
    DataIo,
    DatastreamMapping,
    DeploymentDefaults,
    IOConfig,
    SchemasConfig,
    SmartAppConfig,
    SmartAppFlags,
    SmartAppParams,
)


def test_convert_smart_app_to_manifest():
    """Test successful conversion of SmartAppConfig to AppManifest with updated parameters"""
    config = SmartAppConfig(
        name="test-smart-app",
        title="Test Smart App",
        description="A smart app",
        type="app",
        version="1.0.0",
        category="optimizer",
        flags=SmartAppFlags(),
        data_streams=DataIo(
            inputs=[IOConfig(name="input1", data_type="string", unit="unit1")],
            outputs=[IOConfig(name="output1", data_type="number", unit="unit2")],
        ),
        control_changes=DataIo(
            inputs=[IOConfig(name="control_input", data_type="boolean", unit="unit3")],
            outputs=[IOConfig(name="control_output", data_type="string", unit="unit4")],
        ),
        parameters=[
            SmartAppParams(name="param1", data_type="number"),
            SmartAppParams(name="param2", data_type="string"),
        ],
        ui_schemas=SchemasConfig(configuration="schemas/configuration.json", parameters="schemas/parameters.json"),
        defaults=DeploymentDefaults(
            system={"env": "production"},
            datastream_mapping=[DatastreamMapping(app="input1", datastream="stream1")],
            configuration={"key": "value"},
            parameters={"param1": 42, "param2": "default"},
        ),
        custom_actions=CustomActionsIO(
            inputs=[CustomActionDef(type="input_action")],
            outputs=[CustomActionDef(type="output_action")],
        ),
    )

    manifest = config.to_manifest(read_schemas=True, workdir=Path(__file__).parent)

    # Check basic properties
    assert manifest.name == "test-smart-app"
    assert manifest.title == "Test Smart App"
    assert manifest.description == "A smart app"
    assert manifest.type == AppTypes.app
    assert manifest.version == "1.0.0"
    assert manifest.category == "optimizer"

    # Check parameters
    assert len(manifest.parameters) == 2
    assert any(p.name == "param1" and p.data_type == "number" and p.default == 42 for p in manifest.parameters)
    assert any(p.name == "param2" and p.data_type == "string" and p.default == "default" for p in manifest.parameters)

    # Check flags
    assert manifest.flags.spec_version == "5.0.0"
    assert manifest.flags.resources_required is True

    # Check IO mappings
    assert len(manifest.io) == 4
    assert any(io.name == "input1" and io.way == IOWay.input for io in manifest.io)
    assert any(io.name == "output1" and io.way == IOWay.output for io in manifest.io)
    assert any(io.name == "control_input" and io.way == IOWay.input_cc for io in manifest.io)
    assert any(io.name == "control_output" and io.way == IOWay.output_cc for io in manifest.io)

    # Check schemas
    assert manifest.schemas.configuration == {"configuration_schema": {"test1": "string"}}
    assert manifest.schemas.parameters == {"parameters_schema": {"test2": "string"}}

    # Check defaults
    assert manifest.defaults.app.configuration == {"key": "value"}
    assert manifest.defaults.system == {"env": "production"}

    # Validate custom actions
    assert len(manifest.custom_actions) == 2
    assert manifest.custom_actions[0].type == "input_action"
    assert manifest.custom_actions[0].way == "input-ca"
    assert manifest.custom_actions[1].type == "output_action"
    assert manifest.custom_actions[1].way == "output-ca"


def test_conflicting_io_in_inputs_and_input_control():
    """Test that conflicting IO defined in inputs and input control changes raises a ConfigError"""
    config = SmartAppConfig(
        name="conflict-smart-app",
        title="Conflict Smart App",
        description="A smart app",
        type="app",
        version="1.0.0",
        data_streams=DataIo(
            inputs=[IOConfig(name="conflict_io", data_type="string", unit="unit1")],
        ),
        control_changes=DataIo(
            inputs=[IOConfig(name="conflict_io", data_type="number", unit="unit1")],  # Conflict in data_type
        ),
        ui_schemas=SchemasConfig(),
        defaults=DeploymentDefaults(),
    )

    with pytest.raises(ConfigError, match="IO conflict_io has different data type"):
        config.to_manifest(config)


def test_conflicting_data_type_and_unit_on_output_and_input_control():
    """Test conflict on different data_type and units between outputs and input control changes"""
    config = SmartAppConfig(
        name="conflict-smart-app",
        title="Conflict Smart App",
        description="A smart app",
        type="app",
        version="1.0.0",
        data_streams=DataIo(
            outputs=[IOConfig(name="conflict_io", data_type="string", unit="unit1")],
        ),
        control_changes=DataIo(
            inputs=[IOConfig(name="conflict_io", data_type="string", unit="unit2")],  # Conflict in unit
        ),
        ui_schemas=SchemasConfig(),
        defaults=DeploymentDefaults(),
    )

    with pytest.raises(ConfigError, match="IO conflict_io has different unit in data streams and control changes"):
        config.to_manifest(config)


def test_conflicting_io_output_and_output_control():
    """Test conflict between output and output control changes"""
    config = SmartAppConfig(
        name="conflict-smart-app",
        title="Conflict Smart App",
        description="A smart app",
        type="app",
        version="1.0.0",
        data_streams=DataIo(
            outputs=[IOConfig(name="conflict_io", data_type="string", unit="unit1")],
        ),
        control_changes=DataIo(
            outputs=[
                IOConfig(name="conflict_io", data_type="string", unit="unit1")
            ],  # Duplicate in outputs and output control
        ),
        ui_schemas=SchemasConfig(),
        defaults=DeploymentDefaults(),
    )

    with pytest.raises(ConfigError, match="IO conflict_io is defined as output and output control changes"):
        config.to_manifest(config)


def test_schema_do_not_exists():
    """Test schema not found raises ConfigError"""
    config = SmartAppConfig(
        name="test-smart-app",
        title="Test Smart App",
        description="A smart app",
        type="app",
        version="1.0.0",
        ui_schemas=SchemasConfig(configuration="not-found.json", parameters="not-found.json"),
    )

    config.to_manifest(read_schemas=False)  # No exception should be raised

    with pytest.raises(ConfigError, match="Schema file not-found.json does not exist."):
        config.to_manifest(read_schemas=True)
