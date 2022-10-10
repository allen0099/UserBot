import logging

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message

from bot import Bot
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(
    filters.command("count", prefixes=COMMAND_PREFIXES)
    & filters.me
    & ~filters.forwarded
)
@event_log()
async def counting(cli: Bot, msg: Message) -> None:
    await msg.delete()

    m: Message = await msg.reply_text("Counting...")

    count: dict[str | ChatType, int] = {
        "TOTAL": 0,
        ChatType.PRIVATE: 0,
        ChatType.BOT: 0,
        ChatType.GROUP: 0,
        ChatType.SUPERGROUP: 0,
        ChatType.CHANNEL: 0,
    }

    async for dialog in cli.get_dialogs():
        count["TOTAL"] += 1
        count[dialog.chat.type] += 1

    message: str = f""

    for chat_type, count in count.items():
        message += f"{chat_type.capitalize() if isinstance(chat_type, str) else chat_type.name.capitalize()}: <code>{count}</code>\n"

    await m.edit(message)
