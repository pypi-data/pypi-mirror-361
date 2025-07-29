from __future__ import annotations

import asyncio
from typing import List, Optional

from pydantic import BaseModel

from kelvin.application import KelvinApp, Datastream
from kelvin.krn import KRNAssetDataStream
from kelvin.logs import logger
from kelvin.message import Message
from kelvin.publisher.server import MessageData
from kelvin.publisher.csv_publisher import CSVPublisher
from datetime import datetime
from typing import Any, Type, Union

def string_to_strict_type(value: Any, data_type: Type) -> Union[bool, float, str, dict]:
    if isinstance(value, data_type):
        return value
    if data_type is bool:
        return str(value).lower() in ["true", "1"]
    if data_type is float:
        return float(value)
    return value

def message_from_message_data(data: MessageData, outputs: List[Datastream]) -> Optional[Message]:
    output = next((output for output in outputs if output.name == data.resource.data_stream), None)
    if output is None:
        logger.error("csv metric not found in outputs", metric=data.resource)
        return None
    
    msg = Message(
        type=output.type,
        timestamp=data.timestamp or datetime.now().astimezone(),
        resource=data.resource
    )
    msg.payload = string_to_strict_type(data.value, type(msg.payload))
    return msg


class AppConfiguration(BaseModel):
    model_config = {"extra": "allow"}

    csv: str
    replay: bool = False


async def main() -> None:
    app = KelvinApp()
    await app.connect()

    assets = list(app.assets.keys())
    custom_config = AppConfiguration.model_validate(app.app_configuration)
    publisher = CSVPublisher(custom_config.csv, None, True)

    first_run = True
    while first_run or custom_config.replay:
        first_run = False
        async for data in publisher.run():
            for asset in assets:
                data.resource = KRNAssetDataStream(asset, data.resource.data_stream)
                msg = message_from_message_data(data, app.outputs)
                if msg is not None:
                    await app.publish(msg)


if __name__ == "__main__":
    asyncio.run(main())
