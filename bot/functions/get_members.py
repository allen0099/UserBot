import logging

from pyrogram import Client
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import ChatMember

log: logging.Logger = logging.getLogger(__name__)


async def get_members(cli: Client, chat_id: int, limit: int = 10000, choose: str = Filters.RECENT) -> list[ChatMember]:
    offset: int = 0
    members: list[ChatMember] = []

    _stop: bool = False
    while offset < limit and not _stop:
        log.debug(f"Getting {offset} ~ {offset + 200} in {chat_id}")
        members += [_ for _ in await cli.get_chat_members(chat_id, offset=offset, filter=choose)
                    if _.user.id not in {_.user.id: _ for _ in members}.keys()]
        if offset == len(members):
            log.debug("All members returned, stop counting...")
            log.debug(f"Members count: {len(members)}, Filters type: {choose}")
            _stop = True
        offset = len(members)
    return members
