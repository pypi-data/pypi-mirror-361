import asyncio
from datetime import timedelta

from kelvin.application import KelvinApp
from kelvin.krn import KRNAsset
from kelvin.message import CustomAction, Recommendation


class CustomActionApp:
    def __init__(self, app: KelvinApp = KelvinApp()) -> None:
        self.app = app
        self.app.on_custom_action = self.on_custom_action

    async def on_custom_action(self, action: CustomAction) -> None:
        """Callback when a Custom Action is received."""
        print("Received Custom Action: ", action)

        await self.app.publish(action.result(success=True, message="Custom Action applied"))
        # OR
        # await self.app.publish(
        #     CustomActionAckMsg(
        #         resource=action.resource,
        #         payload={
        #             "id": action._msg.id,
        #             "success": True,
        #             "message": "Custom Action applied",
        #         },
        #     )
        # )

    async def publisher_task(self) -> None:
        i = 0
        while True:
            await self.app.publish(
                CustomAction(
                    resource=KRNAsset("test-asset-1"),
                    trace_id=f"trace-{i}",
                    type="example-out",
                    title=f"Test Action {i}",
                    description=f"This is the test action number {i}",
                    expiration_date=timedelta(seconds=30),
                    payload={"big": "payload", "action number": i},
                )
            )

            await asyncio.sleep(1)

            await self.app.publish(
                Recommendation(
                    resource=KRNAsset("test-asset-1"),
                    type="test-recommendation",
                    description=f"This is the recommendation number {i}",
                    expiration_date=timedelta(minutes=5),
                    trace_id=f"rec-trace-{i}",
                    actions=[
                        CustomAction(
                            resource=KRNAsset("test-asset-1"),
                            type="example-out-2",
                            title=f"Test Action {i}",
                            description=f"This is the test action number {i}",
                            expiration_date=timedelta(minutes=5),
                            payload={"big": "payload", "action number": i},
                        )
                    ],
                    auto_accepted=True,
                )
            )

            i += 1
            await asyncio.sleep(5)

    async def run(self) -> None:
        """Run the app."""
        await self.app.connect()
        await self.publisher_task()


if __name__ == "__main__":
    app = CustomActionApp()
    asyncio.run(app.run())
