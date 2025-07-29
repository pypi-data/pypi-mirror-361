import json

from kelvin.krn import KRNAsset
from kelvin.message import Recommendation
from kelvin.message.evidences import LineChart


def test_chart_evidence_serialization() -> None:
    asset = "asset-1"
    linechart = LineChart(
        title=f"Temperature {asset}",
        x_axis={"type": "datetime", "title": {"text": "Date"}},
        y_axis={
            "title": {"text": "Temperature"},
            "plotLines": [
                {
                    "value": 50,
                    "color": "red",
                    "dashStyle": "Solid",
                    "width": 2,
                    "label": {
                        "text": "Limit 50",
                        "align": "right",
                        "style": {"color": "red"},
                    },
                }
            ],
        },
        series=[
            {
                "data": [
                    [1739546257000, 54.431399999677716],
                ],
                "name": "Temperature",
                "type": "line",
            },
            {
                "data": [
                    [1739546257000, 54.09299999967773],
                ],
                "marker": {"enabled": False},
                "name": "Temperature Mean",
                "type": "line",
            },
        ],
    )
    rec = Recommendation(
        resource=KRNAsset(asset),
        type="decrease",
        evidences=[linechart],
    )
    rec_dict = json.loads(rec.to_message().encode().decode())
    assert rec_dict["payload"] == {
        "resource": "krn:asset:asset-1",
        "type": "decrease",
        "actions": {"control_changes": [], "custom_actions": []},
        "evidences": [
            {
                "type": "line-chart",
                "payload": {
                    "title": "Temperature asset-1",
                    "xAxis": {"type": "datetime", "title": {"text": "Date"}},
                    "yAxis": {
                        "title": {"text": "Temperature"},
                        "plotLines": [
                            {
                                "value": 50,
                                "color": "red",
                                "dashStyle": "Solid",
                                "width": 2,
                                "label": {"text": "Limit 50", "align": "right", "style": {"color": "red"}},
                            }
                        ],
                    },
                    "series": [
                        {"name": "Temperature", "type": "line", "data": [[1739546257000, 54.431399999677716]]},
                        {
                            "name": "Temperature Mean",
                            "type": "line",
                            "data": [[1739546257000, 54.09299999967773]],
                            "marker": {"enabled": False},
                        },
                    ],
                },
            }
        ],
    }
