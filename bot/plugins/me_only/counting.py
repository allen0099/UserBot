import logging

from pyrogram import Client, filters, types
from pyrogram.enums import ChatType

from bot import Bot
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("count", prefixes=COMMAND_PREFIXES)
    & filters.me
    & ~filters.forwarded
)
@event_log()
async def counting(cli: Bot, msg: types.Message) -> None:
    await msg.delete()

    m: types.Message = await msg.reply_text("Counting...")

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

    for t, count in count.items():
        message += (
            f"{t.capitalize() if isinstance(t, str) else t.name.capitalize()}"
            f": <code>{count}</code>\n"
        )

    await m.edit(message)
