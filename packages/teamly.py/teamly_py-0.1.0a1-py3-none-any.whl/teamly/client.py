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

import asyncio

from .http import HTTPClient
from .gateway import TeamlyWebSocket
from .state import ConnectionState

from loguru import logger
from typing import (
    Dict,
    List,

    TypeVar,
    Callable,
    Coroutine,
    Any
)

__all__ = (
    'Client',
)

T = TypeVar('T')
Coro = Coroutine[Any,Any, T]
CoroT = TypeVar('CoroT', bound=Callable[..., Coro[Any]])

class _LoopSentinel:
    __slots__ = ()

    def __getattr__(self, attr: str) -> None:
        msg = (
            'loop attribute cannot be accessed in non-async contexts. '
            'Consider using either an asynchronous main function and passing it to asyncio.run or '
            'using asynchronous initialisation hooks such as Client.setup_hook'
        )
        raise AttributeError(msg)

_loop: Any = _LoopSentinel()


class Client:

    def __init__(self) -> None:
        self.loop: asyncio.AbstractEventLoop = _loop
        self.http: HTTPClient = HTTPClient(self.loop)
        self.ws: TeamlyWebSocket = None #type: ignore
        self._listener: Dict[str,List[str]] = {}

        self._connection: ConnectionState = self._get_state()

    def run(self, token: str) -> None:
        """
            Starts the asynchronous event loop with the given token.

            This method initializes and runs the main coroutine (`runner`),
            which currently contains a temporary sleep call for testing purposes.
            In a production environment, this would be replaced with actual logic.

            Args:
                token (str): The token used to authenticate or start the process.
        """

        logger.debug('Your token is "{}"', token)

        async def runner():
            logger.debug("starting coroutine")
            async with self:
                await self.start(token)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            pass

    async def start(self, token: str) -> None:
        await self.http.static_login(token)
        await self.connect()

    async def connect(self) -> None:
        try:
            coro = TeamlyWebSocket.from_client(self)
            self.ws = await asyncio.wait_for(coro,timeout=30)
            while True: #temporaly
                await self.ws.poll_event()
                await asyncio.sleep(1)
        except Exception as e:
            logger.error("Exception error: {}",e)
            await self.close()

    def event(self, coro: CoroT, /) -> CoroT:
        """
            The `event` decorator registers a coroutine function as an event handler.

            This method checks whether the given function is a coroutine. If it is,
            it sets the coroutine as an attribute of the instance, allowing it to be
            called or referenced later as an event. Otherwise, it raises a TypeError.

            Args:
                coro (CoroT): A coroutine function to be registered as an event.

            Returns:
                CoroT: The same coroutine function, unmodified.

            Raises:
                TypeError: If the provided function is not a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function")

        setattr(self, coro.__name__, coro)
        logger.debug("\"{}\" has successfully been registered as an event",coro.__name__)
        return coro

    async def _run_event(
        self,
        coro: Callable[...,Coroutine[Any,Any,Any]],
        event_name: str,
        *arg: Any,
        **kwargs: Any
    ) -> None:
        try:
            await coro(*arg, **kwargs)
        except Exception as e:
            logger.error("The event could not run {}",e)

    def _schedul_event(
        self,
        coro: Callable[..., Coroutine[Any,Any,Any]],
        event_name: str,
        *arg,
        **kwargs
    ) -> asyncio.Task:
        wrapper = self._run_event(coro, event_name, *arg, **kwargs)
        #scheduls event
        return self.loop.create_task(wrapper, name=f"Teamly.py: {event_name}")

    def dispatch(self, event: str, /, *arg: Any, **kwargs: Any):
        method = 'on_' + event

        try:
            coro = getattr(self,method)
        except AttributeError:
            pass
        else:
            self._schedul_event(coro, method, *arg, **kwargs)


    async def _async_setup_hook(self):
        logger.debug("setup event loop...")
        loop = asyncio.get_running_loop()
        self.loop = loop
        self.http.loop = loop

    async def close(self):
        if self.ws is not None:
            await self.ws.close()
        await self.http.close()

    def _get_state(self):
        return ConnectionState(dispatch=self.dispatch,http=self.http)

    @property
    def user(self):
        pass

    async def __aenter__(self):
        logger.debug("Entering context...")
        await self._async_setup_hook()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logger.debug("Exiting context...")
        await self.close()
