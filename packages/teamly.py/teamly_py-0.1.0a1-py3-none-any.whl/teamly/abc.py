
from __future__ import annotations

from enum import Enum
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from .message import Attachment
    from .embed import Embed

class ChannelType(str, Enum):
    TEXT = 'text'
    VOICE = 'voice'
    TODO = 'todo'
    WATCHSTREAM = 'watchstream'
    ANNOUNCEMENT = 'announcement'

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value

class Status(int,Enum):
    OFFLINE = 0
    ONLINE = 1
    IDLE = 2
    DO_DO_DISTURB = 3



class MessageAble:



    async def send(
        self,
        content: str,
        embeds: Optional[Embed],
        attachment: Optional[Attachment],
        replyTo: str
    ):
        pass
