from kelvin.message.msg_type import KMessageType, KMessageTypeAction, KMessageTypeActionAck


def test_action_message_type() -> None:
    """Test action message type."""

    # create action type
    type1 = KMessageTypeAction(action_type="start")
    assert type1.msg_type == "custom-action-create"
    assert type1.type == "start"
    assert type1.encode() == "custom-action-create;type=start"

    # parsing action type
    type2 = KMessageType.from_string("custom-action-create;type=start")
    assert isinstance(type2, KMessageTypeAction)
    assert type2.msg_type == "custom-action-create"
    assert type2.type == "start"

    # parsing action type
    type3 = KMessageType.from_string("custom-action-create")
    assert isinstance(type2, KMessageTypeAction)
    assert type3.msg_type == "custom-action-create"
    assert type3.encode() == "custom-action-create"

    # test quoting
    type4 = KMessageTypeAction(action_type="foo bar")
    assert type4.msg_type == "custom-action-create"
    assert type4.type == "foo bar"
    assert type4.encode() == "custom-action-create;type=foo bar"

    # parsing quoted action type
    type5 = KMessageType.from_string("custom-action-create;type=foo bar")
    assert isinstance(type5, KMessageTypeAction)
    assert type5.msg_type == "custom-action-create"
    assert type5.type == "foo bar"


def test_action_ack_message_type() -> None:
    """Test action ack message type."""

    # create action ack type
    type1 = KMessageTypeActionAck()
    assert type1.msg_type == "custom-action-result"
    assert type1.encode() == "custom-action-result"

    # parsing action ack type
    type2 = KMessageType.from_string("custom-action-result")
    assert isinstance(type2, KMessageTypeActionAck)
    assert type2.msg_type == "custom-action-result"
    assert type2.encode() == "custom-action-result"
