import logging
import math
import subprocess
from datetime import datetime, timedelta

import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message

from main import user_bot

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("info", prefixes="$") & filters.me & ~ filters.forwarded)
async def info(_: Client, msg: Message) -> None:
    diff_check: str = subprocess.check_output(["git", "diff"]).strip().decode("utf-8")
    label: str = subprocess.check_output(["git", "describe", "--always"]).strip().decode("utf-8")

    if diff_check != '':
        label += " (modified)"

    await msg.reply_text(f"<b>AllenUserBot</b> <code>v{user_bot.app_version}</code>\n"
                         f"<b>Language</b>: <code>Python</code>\n"
                         f"<b>Library</b>: <code>Pyrogram/{pyrogram.__version__}</code>\n"
                         f"<b>Uptime</b>: <code>{await _parse_time()}</code>\n"
                         f"<b>Memory</b>: <code>{user_bot.process.memory_info().rss / 1024 / 1024} MiB</code>\n"
                         f"<b>Git revision number</b>: <code>{label}</code>")


async def _parse_time() -> str:
    ti: timedelta = datetime.utcnow() - user_bot.start_time

    _days: int = math.floor(ti.total_seconds() / 86400)
    ti -= timedelta(days=_days, microseconds=ti.microseconds)

    _hours, _min, _seconds = str(ti).split(":")

    _r: str = f""
    if _days > 0:
        _r += f"{_days} days "
    if int(_hours) > 0:
        _r += f"{int(_hours)} hours "
    if int(_min) > 0:
        _r += f"{int(_min)} minutes "
    _r += f"{int(_seconds)} seconds"
    return _r.lstrip()
