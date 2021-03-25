import logging

from pyrogram import Client, filters
from pyrogram.types import Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("count", prefixes="$") & filters.me & ~ filters.forwarded)
async def dialogs_count(cli: Client, msg: Message) -> None:
    count: dict = {
        "total": 0,
        "group": 0,
        "supergroup": 0,
        "channel": 0,
        "private": 0,
        "bot": 0
    }

    async for dialog in cli.iter_dialogs():
        count["total"] += 1
        count[dialog.chat.type] += 1

    await msg.reply_text(f"Total: <code>{count['total']}</code>\n"
                         f"Groups: <code>{count['group']}</code>\n"
                         f"Super groups: <code>{count['supergroup']}</code>\n"
                         f"Channel: <code>{count['channel']}</code>\n"
                         f"Private: <code>{count['private']}</code>\n"
                         f"Bot: <code>{count['bot']}</code>\n")
