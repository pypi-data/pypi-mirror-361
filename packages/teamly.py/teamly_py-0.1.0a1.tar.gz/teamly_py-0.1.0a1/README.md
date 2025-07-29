# Teamly.py

**Teamly.py** is a modern asynchronous Python wrapper for the Teamly API. The library is still under heavy development and many features are in progress.

## Current Progress

The following pieces are already implemented:

- **HTTP client** covering most Teamly endpoints such as channels, messages, roles, todos and more.
- **WebSocket gateway** for real-time events with a keep-alive handler.
- **Event system** using the `Client.event` decorator and `dispatch` method.
- **Connection state parser** that maps gateway events to your callbacks.
- Basic context manager support on the `Client` class.

## Planned Work

Work is ongoing on these areas:

- Expanding event parsing and improving the gateway.
- Automatic reconnection and error handling.
- HTTP rate limit management.
- Command framework for building bots.
- Stronger type hints and data models.
- More examples and tests.

## Quick Example

```python
from teamly import Client

client = Client()

@client.event
async def on_ready():
    print("Bot ready!")

client.run("YOUR_TOKEN_HERE")
```

## Installation

Although not feature complete, the package can be installed with pip:

```bash
pip install teamly.py
```

## License

This project is licensed under the MIT License.
