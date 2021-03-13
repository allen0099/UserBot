import logging
import re
from typing import Union

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.functions import get_full
from database.models import User

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("req", prefixes="$") & filters.me & ~ filters.forwarded)
async def request(cli: Client, msg: Message) -> None:
    log.debug(f"{msg.from_user.id} issued command request")
    log.debug(f" -> text: {msg.text}")

    try:
        peer_id: str = re.search(re.compile(r"(?<=@)?\w{5,}$|^[+-]?\d+$|(?:me|self)$"), msg.command[1])[0]
        log.debug(f"Peer id: {peer_id}")
    except (IndexError, TypeError):
        await cli.send_message("me", "Usage: <code>$req &lt;uid|username&gt;</code>")
        return
    else:
        data: Union[User] = await get_full(cli, peer_id)
        if isinstance(data, User):
            await cli.send_message("me", str(data.first_name))
        else:
            await cli.send_message("me", "Not yet support")
