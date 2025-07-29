import whitebox
import asyncio
import websockets
import json
import functools
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Time to wait before reconnecting to the websocket
RECONNECT_SLEEP_TIME: int = 2


async def should_emit(emit_every: int | None = None, last_emit_on: int = 0):
    if emit_every is None:
        return True

    now = asyncio.get_event_loop().time()
    if now - last_emit_on >= emit_every:
        last_emit_on = now
        return True

    return False


def websocket_handler(endpoint: str, emit_every: int | None = None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            ws_url = f"{self.STRATUX_URL}/{endpoint}"

            last_emit_on = (
                asyncio.get_event_loop().time() - 0
                if emit_every is None
                else emit_every
            )

            while self.is_active:
                try:
                    async with websockets.connect(
                        ws_url, ping_timeout=None, close_timeout=None
                    ) as websocket:
                        while self.is_active:
                            try:
                                message = await websocket.recv()
                                data = json.loads(message)

                                if not await should_emit(emit_every, last_emit_on):
                                    continue

                                if data:
                                    last_emit_on = asyncio.get_event_loop().time()
                                    await func(self, data)

                            except websockets.exceptions.ConnectionClosed:
                                logger.exception("Connection closed")
                                break
                            except json.JSONDecodeError:
                                logger.exception("Failed to decode JSON")
                                continue
                except Exception:
                    logger.exception("Exception in websocket handler")
                    await asyncio.sleep(RECONNECT_SLEEP_TIME)

        return wrapper

    return decorator


class WhiteboxPluginStratux(whitebox.Plugin):
    name = "Stratux"

    def __init__(self):
        self.STRATUX_URL = os.getenv("STRATUX_URL", "ws://stratux:80")

        self.is_active = False
        self.traffic_task = None
        self.situation_task = None
        self.status_task = None

        self.whitebox.register_event_callback("flight_start", self.on_flight_start)
        self.whitebox.register_event_callback("flight_end", self.on_flight_end)

    async def on_flight_start(self, data):
        self.is_active = True

        if self.traffic_task is None or self.traffic_task.done():
            self.traffic_task = asyncio.create_task(self.gather_traffic())

        if self.situation_task is None or self.situation_task.done():
            self.situation_task = asyncio.create_task(self.gather_situation())

        if self.status_task is None or self.status_task.done():
            self.status_task = asyncio.create_task(self.gather_status())

    async def on_flight_end(self, data):
        self.is_active = False

        if self.traffic_task:
            self.traffic_task.cancel()
            self.traffic_task = None

        if self.situation_task:
            self.situation_task.cancel()
            self.situation_task = None

        if self.status_task:
            self.status_task.cancel()
            self.status_task = None

    @websocket_handler("situation", emit_every=2)
    async def gather_situation(self, situation_data):
        """
        Note: Situation data emit is throttled because it is updated very frequently
        """

        await self.whitebox.api.location.emit_location_update(
            situation_data.get("GPSLatitude"),
            situation_data.get("GPSLongitude"),
            situation_data.get("GPSAltitudeMSL"),
        )

    @websocket_handler("traffic")
    async def gather_traffic(self, traffic_data):
        await self.whitebox.api.traffic.emit_traffic_update(traffic_data)

    @websocket_handler("status")
    async def gather_status(self, status_data):
        await self.whitebox.api.status.emit_status_update(status_data)


plugin_class = WhiteboxPluginStratux
