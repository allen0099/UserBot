import logging

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

from database import db
from database.privilege import Privilege

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.group, group=-1)
async def privilege(_: Client, msg: Message) -> None:
    """
    Log user privilege when new update income and database not exist.
    """
    if msg.chat.type == ChatType.SUPERGROUP:
        group_id: int = msg.chat.id
        group = db.session.query(Privilege).get(group_id)

        if not group:
            log.debug(f"{msg.chat.title} not found in database, adding...")
            await Privilege.create(msg)
