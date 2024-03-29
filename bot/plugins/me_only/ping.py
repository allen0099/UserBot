import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from bot import Bot
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


# 先合併裡面的，回傳 func 往上丟，每一次合併記憶體位置都會不一樣
# 因此，Client.on_message 必須是最外層的 decorator，才能確保前面的東西能被順利執行
@Client.on_message(
    filters.command("ping", prefixes=COMMAND_PREFIXES) & filters.me & ~filters.forwarded
)
@event_log()
async def ping(_: Bot, msg: Message) -> None:
    await msg.reply_text("pong!")
