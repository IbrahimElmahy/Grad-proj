from __future__ import annotations

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class HazardAlertConsumer(AsyncWebsocketConsumer):
    group_name = "runway_alerts"

    async def connect(self) -> None:
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection.established",
                    "group": self.group_name,
                    "message": "Subscribed to runway hazard alerts.",
                }
            )
        )

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        if not text_data:
            return

        payload = json.loads(text_data)
        if payload.get("type") == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def alert_message(self, event: dict) -> None:
        await self.send(text_data=json.dumps(event["payload"]))
