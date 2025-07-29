import pytest

from kelvin.application import KelvinApp
from kelvin.message.base_messages import RuntimeManifest


@pytest.mark.asyncio
async def test_inputs_outputs():
    app = KelvinApp()

    manif = RuntimeManifest(
        resource="krn:ad:asset1/metric1",
        payload={
            "datastreams": [
                {"name": "input-1-datastream", "primitive_type_name": "number"},
                {"name": "input-2-datastream", "primitive_type_name": "boolean"},
                {"name": "input-3-cc-datastream", "primitive_type_name": "string"},
                {"name": "output-cc-3-datastream", "primitive_type_name": "string"},
                {"name": "output-1-datastream", "primitive_type_name": "number"},
                {"name": "output-2-datastream", "primitive_type_name": "boolean"},
            ],
            "resources": [
                {
                    "name": "jg-random-asset",
                    "type": "asset",
                    "properties": {"area": 11, "field": "Eagle Ford", "plc_type": "ABB", "tubing_length": 25},
                    "datastreams": {
                        "input-1-datastream": {"map_to": "input-1", "access": "RO", "owned": False},
                        "input-2-datastream": {"map_to": "input-2", "access": "RO", "owned": False},
                        "input-3-cc-datastream": {"map_to": "input-3-cc", "access": "RW", "owned": True},
                        "output-1-datastream": {"map_to": "output-1", "access": "RO", "owned": True},
                        "output-2-datastream": {"map_to": "output-2", "access": "RO", "owned": True},
                        "output-cc-3-datastream": {"map_to": "output-cc-3", "access": "RW", "owned": False},
                    },
                },
                {
                    "name": "asset2",
                    "type": "asset",
                    "datastreams": {
                        "input-1-datastream": {"map_to": "input-1", "access": "RO", "owned": False},
                        "input-2-datastream": {"map_to": "input-2", "access": "RO", "owned": False},
                        "input-3-cc-datastream": {"map_to": "input-3-cc", "access": "RW", "owned": True},
                        "output-1-datastream": {"map_to": "output-1", "access": "RO", "owned": True},
                        "output-2-datastream": {"map_to": "output-2", "access": "RO", "owned": True},
                        "output-cc-3-datastream": {"map_to": "output-cc-3", "access": "RW", "owned": False},
                    },
                },
            ],
            "configuration": {"max": 100, "min": 0, "period": 60, "random": True},
        },
    )

    await app._process_runtime_manifest(manif)

    assert {i.name for i in app.inputs} == set(["input-1", "input-2", "output-cc-3"])
    assert {o.name for o in app.outputs} == set(["output-1", "output-2", "input-3-cc"])
