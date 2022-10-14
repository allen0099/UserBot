import logging
from enum import Enum

from pyrogram import Client, filters
from pyrogram.types import Message

from bot import Bot
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


class MeOnlyCommandList(Enum):
    # Me only commands
    ADMIN = ("admin", "提及群組內的管理員")
    COUNT = ("count", "取得訊息類型統計")
    EVAL = ("eval", "執行 Python 程式碼")
    GET = ("get", "取得訊息簡短內容")
    HELP = ("help", "取得指令列表")
    INFO = ("info", "取得機器人運行狀態")
    PING = ("ping", "PONG")
    REQUEST = ("req", "取得使用者 / 群組 / 頻道的詳細資訊")
    ROLL = ("roll", "隨機骰或隨機選擇")

    ZH_CN = ("zh", "轉簡體中文")


class AdminOnlyCommandList(Enum):
    # Admin only commands (Not implemented yet)
    BAIL = ("bail", "清除本群所有封鎖或受限制成員的限制")
    BAN = ("ban", "封鎖使用者")
    DELETE_MESSAGE = ("del", "從回覆的訊息刪除到最後一條，或刪除指定連結之間的訊息")
    KICK = ("kick", "踢出使用者")
    KILLDA = ("killda", "清理已刪除的帳號")
    MUTE = ("mute", "禁言使用者")


@Client.on_message(
    filters.command("help", prefixes=COMMAND_PREFIXES) & filters.me & ~filters.forwarded
)
@event_log()
async def help_commands(_: Bot, msg: Message):
    text: str = (
        "<b><u>AllenUserBot Help Table</u></b>\n"
        "\n"
        f"可用指令前綴 <code>{COMMAND_PREFIXES}</code>\n"
    )

    text += f"<b>Me only commands</b>\n"
    for command in MeOnlyCommandList:
        text += f"<code> {command.value[0]}</code> - {command.value[1]}\n"

    text += f"\n<b>Admin only commands</b>\n"
    for command in AdminOnlyCommandList:
        text += f"<code> {command.value[0]}</code> - {command.value[1]}\n"

    await msg.reply_text(text)
