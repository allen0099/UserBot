import asyncio
import html
import logging
from datetime import datetime
from typing import Optional

from pyrogram import Client
from pyrogram.errors import PeerIdInvalid
from pyrogram.types import Chat

from .resolve_peer import resolve_peer
from ..types import EMOJI

log: logging.Logger = logging.getLogger(__name__)


def get_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def get_mention_name(uid: int, first_name: str, last_name: str = None) -> str:
    return f"<a href='tg://user?id={uid}'>" \
           f"{html.escape(first_name) if first_name else EMOJI.empty}" \
           f"{' ' + html.escape(last_name) if last_name else EMOJI.empty}</a>"


async def get_common_chats(cli: Client, uid: int) -> list[Chat]:
    inviter_commons: Optional[list[Chat]] = None
    times = 1
    while not inviter_commons:
        try:
            inviter_commons = await cli.get_common_chats(uid)
        except PeerIdInvalid:
            times += 1
            if times >= 5:
                raise ValueError("Max retries exceeded!")
            log.debug(f"Can't get common chats with {uid}, this is {times} times try...")
            await asyncio.sleep(5)
        return inviter_commons
