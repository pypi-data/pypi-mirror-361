import asyncio
from datetime import timedelta
from typing import AsyncGenerator

from kelvin.message import CustomAction, CustomActionMsg
from kelvin.publisher import DataGenerator


class CustomActionGenerator(DataGenerator):
    def __init__(self) -> None:
        print("Hello from MyGenerator")

    async def run(self) -> AsyncGenerator[CustomActionMsg, None]:
        print("Running MyGenerator")

        for i in range(10):
            msg = CustomAction(
                resource="krn:asset:test-asset-1",
                expiration_date=timedelta(seconds=30),
                type="example-in",
                title="hello generator",
                description="big description",
                payload={"big": "payload"},
            )

            print("msg", msg)

            yield msg
            await asyncio.sleep(1)
