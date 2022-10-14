import logging
import math
import subprocess
from datetime import datetime, timedelta

import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message

from bot import Bot
from bot.plugins import COMMAND_PREFIXES
from core import main_logger
from core.decorator import event_log

log: logging.Logger = main_logger(__name__)


@Client.on_message(
    filters.command("info", prefixes=COMMAND_PREFIXES) & filters.me & ~filters.forwarded
)
@event_log()
async def info(cli: Bot, msg: Message) -> None:
    clean_check: str = (
        subprocess.check_output(["git", "diff", "--stat"]).strip().decode("utf-8")
    )
    current_revision: str = (
        subprocess.check_output(["git", "describe", "--always"]).strip().decode("utf-8")
    )

    if clean_check != "":
        current_revision += " (modified)"

    await msg.reply_text(
        f"<b><u>AllenUserBot</u></b>\n"
        f"<b>套件庫版本：</b><code>Pyrogram/{pyrogram.__version__}</code>\n"
        f"<b>運行總時間：</b><code>{await _parse_time(cli)}</code>\n"
        f"<b>記憶體用量 (RSS)：</b><code>"
        f"{pretty_memory_size(cli.process.memory_info().rss)}</code>\n"
        f"<b>Git 版本：</b><code>{current_revision}</code>"
    )


def pretty_memory_size(calc_bytes: int):
    metric: tuple[str, str, str, str, str] = ("B", "KB", "MB", "GB", "TB")

    if calc_bytes == 0:
        return "0 B"

    nunit: int = int(math.floor(math.log(calc_bytes, 1024)))
    size: float = round(calc_bytes / (math.pow(1024, nunit)), 2)

    return f"{format(size, '.2f')} {metric[nunit]}"


async def _parse_time(bot: Bot) -> str:
    ti: timedelta = datetime.now() - datetime.fromtimestamp(bot.process.create_time())

    _days: int = math.floor(ti.total_seconds() / 86400)
    ti -= timedelta(days=_days, microseconds=ti.microseconds)

    _hours, _min, _seconds = str(ti).split(":")

    _r: str = f""
    if _days > 0:
        _r += f"{_days} 天 "
    if int(_hours) > 0:
        _r += f"{int(_hours)} 小時 "
    if int(_min) > 0:
        _r += f"{int(_min)} 分鐘 "
    _r += f"{int(_seconds)} 秒"
    return _r.lstrip()
