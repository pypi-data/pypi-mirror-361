"""Test Message Builders"""

import uuid
from datetime import datetime, timedelta

from kelvin.krn import KRNAsset, KRNAssetDataStream
from kelvin.message import (
    ControlAck,
    ControlChange,
    ControlChangeMsg,
    CustomAction,
    CustomActionMsg,
    CustomActionResult,
    CustomActionResultMsg,
    DataTag,
    Recommendation,
    RecommendationMsg,
)
from kelvin.message.base_messages import ControlChangeAck


def test_builder_control_change() -> None:
    now = datetime.now()

    cc = ControlChange(
        resource=KRNAssetDataStream("asset1", "metric1"), expiration_date=now, payload=25, trace_id="potalto trace id"
    )

    cc_msg = cc.to_message()

    assert isinstance(cc_msg, ControlChangeMsg)
    assert cc_msg.payload.expiration_date == cc.expiration_date
    assert cc_msg.payload.payload == cc.payload
    assert cc_msg.resource == cc.resource


def test_builder_recommendation() -> None:
    now = datetime.now()
    cc_uuid = uuid.uuid4()

    cc = ControlChange(
        resource=KRNAssetDataStream("asset1", "metric1"), expiration_date=now, payload=25, control_change_id=cc_uuid
    )

    rec = Recommendation(
        resource=KRNAsset("asset1"),
        type="e2e_recommendation",
        control_changes=[cc],
        expiration_date=timedelta(minutes=5),
        metadata={"key": "value"},
        auto_accepted=True,
        custom_identifier="custom_id",
        trace_id="trace",
    )

    rec_msg = rec.to_message()
    assert isinstance(rec_msg, RecommendationMsg)
    assert rec_msg.trace_id == "trace"
    assert rec_msg.payload.metadata == rec.metadata
    assert rec_msg.payload.custom_identifier == rec.custom_identifier
    assert rec_msg.payload.state == "auto_accepted"
    assert rec_msg.payload.trace_id == rec.trace_id


def test_builder_data_tag_minimum() -> None:
    now = datetime.now()
    tag_builder = DataTag(start_date=now, tag_name="tag1", resource=KRNAsset("asset1"))
    tag_msg = tag_builder.to_message()

    assert tag_msg.payload.start_date == now
    assert tag_msg.payload.end_date == now
    assert tag_msg.payload.tag_name == "tag1"
    assert tag_msg.resource == tag_msg.payload.resource == KRNAsset("asset1")


def test_builder_data_tag_all() -> None:
    start = datetime.now() - timedelta(minutes=5)
    end = datetime.now()
    tag_builder = DataTag(
        start_date=start,
        end_date=end,
        tag_name="tag1",
        resource=KRNAsset("asset1"),
        description="this is description",
        contexts=[KRNAssetDataStream("asset1", "metric1")],
    )
    tag_msg = tag_builder.to_message()

    assert tag_msg.payload.start_date == start
    assert tag_msg.payload.end_date == end
    assert tag_msg.payload.tag_name == "tag1"
    assert tag_msg.payload.description == "this is description"
    assert tag_msg.payload.contexts == [KRNAssetDataStream("asset1", "metric1")]
    assert tag_msg.resource == tag_msg.payload.resource == KRNAsset("asset1")


def test_custom_action_build() -> None:
    now = datetime.now()

    builder = CustomAction(
        resource="krn:asset:asset-1",
        type="action type",
        expiration_date=now,
        description="action description",
        title="action title",
        trace_id="big trace id",
        payload={"key": "value"},
    )

    msg = builder.to_message()
    assert isinstance(msg, CustomActionMsg)
    assert msg.resource == KRNAsset("asset-1")
    assert msg.trace_id == "big trace id"
    assert msg.type.type == "action type"
    assert msg.payload.expiration_date == now
    assert msg.payload.description == "action description"
    assert msg.payload.title == "action title"
    assert msg.payload.payload == {"key": "value"}


def test_custom_action_result_build() -> None:
    action_id = uuid.uuid4()

    builder = CustomActionResult(
        resource="krn:asset:asset-1",
        action_id=action_id,
        success=True,
        message="action result message",
        metadata={"key": "value"},
    )

    msg = builder.to_message()
    assert isinstance(msg, CustomActionResultMsg)
    assert msg.resource == KRNAsset("asset-1")
    assert msg.payload.id == action_id
    assert msg.payload.success is True
    assert msg.payload.message == "action result message"
    assert msg.payload.metadata == {"key": "value"}


def test_build_control_ack() -> None:
    builder = ControlAck(
        resource=KRNAssetDataStream("asset1", "output-cc-number"),
        state="processed",
        message="status from output-cc-number",
        metadata={"key": "value"},
    )

    msg = builder.to_message()
    assert isinstance(msg, ControlChangeAck)
    assert msg.resource == KRNAssetDataStream("asset1", "output-cc-number")
    assert msg.payload.state == "processed"
    assert msg.payload.message == "status from output-cc-number"
    assert msg.payload.metadata == {"key": "value"}
