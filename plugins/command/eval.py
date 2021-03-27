import html
import logging
import re
import sys
import traceback
from io import StringIO

from pyrogram import Client, filters
from pyrogram.types import Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("eval", prefixes=".") & filters.me)
async def api(_: Client, msg: Message) -> None:
    out: StringIO = StringIO()
    sys.stdout = out
    err: StringIO = StringIO()
    sys.stderr = err

    message: str = f"<b><u>Expression</u></b>\n"
    send: Message = await msg.reply(message, parse_mode="html")

    cmd: str = re.findall(r"(?s)(?<=\.eval ).*", msg.text)[0]

    log.info(f"{msg.from_user.id} exec\n{cmd}")

    # noinspection PyBroadException
    try:
        message += f"<code>{html.escape(cmd)}</code>\n\n"
        await send.edit(message, parse_mode="html")
        eval(compile(cmd, 'tmp_code', 'exec'))
    except Exception:
        lines: list[str] = traceback.format_exc().splitlines()
        print(lines[-1], file=err)

    if out.getvalue() != "":
        message += f"<b><u>Output</u></b>\n" \
                   f"<code>{html.escape(out.getvalue())[0:-1]}</code>\n\n"
        await send.edit(message, parse_mode="html")

    if err.getvalue() != "":
        message += f"<b><u>Error</u></b>\n" \
                   f"<code>{html.escape(err.getvalue())[0:-1]}</code>\n"
        await send.edit(message, parse_mode="html")

    # make sure redirect output to terminal
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
