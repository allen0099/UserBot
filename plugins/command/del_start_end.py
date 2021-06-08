import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.functions import delete_messages

log: logging.Logger = logging.getLogger(__name__)
__USAGE__: str = "Usage: <code>$del &lt;start&gt; &lt;end&gt;</code>"


@Client.on_message(filters.command("del", prefixes="$") & filters.me & filters.group & ~ filters.forwarded)
async def del_messages(cli: Client, msg: Message) -> None:
    if len(msg.command) != 3:
        log.debug("Command not 3")
        await msg.reply(__USAGE__)
        return

    try:
        start: int = int(msg.command[1])
        stop: int = int(msg.command[2])
    except ValueError:
        log.debug("Command not a number")
        await msg.reply(__USAGE__)
        return

    await delete_messages(cli, msg.chat.id, start, stop)
