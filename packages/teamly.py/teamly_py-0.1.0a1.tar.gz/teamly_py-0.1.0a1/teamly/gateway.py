'''
MIT License

Copyright (c) 2025 Fatih Kuloglu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from __future__ import annotations

import asyncio
import threading
import aiohttp
import json
import time

from typing import TYPE_CHECKING, Any, Optional, Dict, Callable
from loguru import logger

from .state import ConnectionState

if TYPE_CHECKING:
    from .client import Client


class GatewayRatelimiter:
    def __init__(self, count: int = 110, per: float = 60.0) -> None:
        # The default is 110 to give room for at least 10 heartbeats per minute
        self.max: int = count
        self.remaining: int = count
        self.window: float = 0.0
        self.per: float = per
        self.lock: asyncio.Lock = asyncio.Lock()

    def is_ratelimited(self) -> bool:
        current = time.time()
        if current > self.window + self.per:
            return False
        return self.remaining == 0

    def get_delay(self) -> float:
        current = time.time()

        if current > self.window + self.per:
            self.remaining = self.max

        if self.remaining == self.max:
            self.window = current

        if self.remaining == 0:
            return self.per - (current - self.window)

        self.remaining -= 1
        return 0.0

    async def block(self) -> None:
        async with self.lock:
            delta = self.get_delay()
            if delta:
                logger.warning('WebSocket is ratelimited, waiting {} seconds',delta)
                await asyncio.sleep(delta)


class KeepAliveHandler(threading.Thread):

    def __init__(self, ws: TeamlyWebSocket,interval: Optional[float] = None):
            super().__init__(daemon=True)
            self.ws: TeamlyWebSocket = ws
            self.interval: Optional[float] = interval
            self.behind_msg: str = 'Can\'t keep up, websocket is {} behind.'
            self._stop_event: threading.Event = threading.Event()
            self._last_send: float = time.perf_counter()
            self._last_ack: float = time.perf_counter()
            self.latency: float = float('inf')

    def run(self):
        while not self._stop_event.wait(self.interval):
            if time.perf_counter() - self._last_ack > self.interval * 2: #type: ignore
                logger.warning("[KeepAliveHandler] ACK not received, connection may be dead.")
                continue

            self._last_send = time.perf_counter()

            data = self.get_payload()
            coro = self.ws.send_heartbeat(data)
            future = asyncio.run_coroutine_threadsafe(coro, self.ws.loop)
            try:
                future.result(timeout=10)
            except Exception as e:
                logger.error("[KeepAliveHandler] send error:", e)

    def get_payload(self) -> Dict[str, Any]:
        return {
            "t": "HEARTBEAT",
            "d": {}
        }

    def stop(self):
        self._stop_event.set()

    def ack(self):
        ack_time = time.perf_counter()
        self._last_ack = ack_time
        self.latency = ack_time - self._last_send
        if self.latency > 10:
            logger.warning(self.behind_msg,self.latency)

    def tick(self):
        pass

class TeamlyWebSocket:

    if TYPE_CHECKING:
        _connection: ConnectionState
        _dispatch_parsers: Dict[str, Callable[..., Any]]

    def __init__(self, socket: aiohttp.ClientWebSocketResponse,*, loop: asyncio.AbstractEventLoop) -> None: #type: ignore
        self.socket: aiohttp.ClientWebSocketResponse = socket
        self._keep_alive: Optional[KeepAliveHandler] = None
        self.loop: asyncio.AbstractEventLoop = loop
        self._close_code: Optional[int] = None

    @classmethod
    async def from_client(cls, client: Client):
        socket = await client.http.ws_connect()
        ws = cls(socket, loop=client.loop)

        ws._connection = client._connection
        ws._dispatch_parsers = client._connection.parsers

        await ws.poll_event()

        return ws

    async def poll_event(self):
        '''
            Continuously polls the WebSocket connection for incoming messages.

            Depending on the message type (text, binary, error, or close),
            it delegates the message to the appropriate handler or logs it.

            This function is meant to be run in an event loop (e.g., inside a task).
        '''

        try:
            msg = await self.socket.receive()
            if msg.type is aiohttp.WSMsgType.TEXT:
                await self.received_message(msg.data)
            elif msg.type is aiohttp.WSMsgType.BINARY:
                await self.received_message(msg.data)
            elif msg.type is aiohttp.WSMsgType.ERROR:
                logger.error("Received: ", msg)
            elif msg.type in (
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING
            ):
                logger.debug("Received: {}",msg)
        except Exception as e:
            logger.error("Exception error {}",e)

    async def received_message(self, msg: Any):
        if type(msg) is bytes:
            msg = msg.decode('utf-8')

        if msg is None:
            return

        msg = json.loads(msg)

        event = msg["t"]
        data = msg["d"]

        # if self._keep_alive:
        #     self._keep_alive.tick()

        if event == "HEARTBEAT_ACK":
            if self._keep_alive:
                self._keep_alive.ack()
            return

        if event == "READY":
            interval = data["heartbeatIntervalMs"] / 1000
            self._keep_alive = KeepAliveHandler(ws=self,interval=interval)
            await self.socket.send_json(self._keep_alive.get_payload())
            self._keep_alive.start()

        try:
            func = self._dispatch_parsers[event]
        except KeyError:
            logger.debug("Unknown event {}",event)
        else:
            func(data)

        #print(json.dumps(msg,indent=4,ensure_ascii=False))

    async def close(self, code: int = 4000) -> None:
        if self._keep_alive:
            self._keep_alive.stop()
            self._keep_alive = None

        self._close_code = code
        await self.socket.close(code=code)

    async def send_heartbeat(self, data: Any):
        await self.socket.send_str(json.dumps(data))
