import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from bot import Bot
from bot.filters import admin_required
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger

log: logging.Logger = event_logger(__name__)
__USAGE__: str = "Usage: <code>$del &lt;start&gt; &lt;end&gt;</code>"


@Client.on_message(
    filters.command("del", prefixes=COMMAND_PREFIXES)
    & admin_required
    & filters.group
    & ~filters.forwarded
)
@event_log()
async def del_messages(cli: Bot, msg: Message) -> None:
    if msg.reply_to_message:
        start: int = msg.reply_to_message.id
        stop: int = msg.id

    elif len(msg.command) == 3:
        start_obj: str = msg.command[1]
        stop_obj: str = msg.command[2]

        if start_obj.startswith("http"):
            # Message link
            start: int = int(start_obj.split("/")[-1])
            stop: int = int(stop_obj.split("/")[-1])

        else:
            try:
                start: int = int(start_obj)
                stop: int = int(stop_obj)

            except ValueError:
                log.debug(f"Invalid message id!, start: {start_obj}, stop: {stop_obj}")
                await msg.reply_text(__USAGE__)
                return

    else:
        await msg.reply_text(__USAGE__)
        return

    log.debug(f"Deleting messages from {start} to {stop} in {msg.chat.id}...")
    await cli.delete_range_messages(msg.chat.id, start, stop)
