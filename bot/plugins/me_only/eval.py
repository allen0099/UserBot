import ast
import html
import logging
import re
import sys
import traceback
from _ast import AST, Module
from io import StringIO

from pyrogram import Client, filters, types
from pyrogram.enums import ParseMode

from bot import Bot
from core import main_logger
from core.decorator import event_log

log: logging.Logger = main_logger(__name__)


# https://stackoverflow.com/a/60934327
@Client.on_message(
    filters.command("eval", prefixes=".") & filters.me & ~filters.forwarded
)
@event_log()
async def api_call(_: Bot, msg: types.Message) -> None:
    message: str = f"<b><u>Expression</u></b>\n"

    cmd: str = re.findall(r"(?s)(?<=\.eval ).*", msg.text)[0]
    message += f"<code>{html.escape(cmd)}</code>\n\n"

    log.info(f"{msg.from_user.id} try to execute\n{cmd}")

    send: types.Message = await msg.reply(message, parse_mode=ParseMode.HTML)

    out: StringIO = StringIO()
    sys.stdout = out
    err: StringIO = StringIO()
    sys.stderr = err

    parsed_fn: AST | Module = ast.parse(
        f"async def __s(cli: Bot, msg: types.Message): pass"
    )

    # noinspection PyBroadException
    try:
        parsed_stmts: AST | Module = ast.parse(cmd)

        for _ in parsed_stmts.body:
            ast.increment_lineno(_)

        # noinspection PyUnresolvedReferences
        parsed_fn.body[0].body = parsed_stmts.body

        exec(compile(parsed_fn, filename="<ast>", mode="exec"), None)
        await eval("__s(_, msg)", None)
    except Exception:
        lines: list[str] = traceback.format_exc().splitlines()
        print(lines[-1], file=err)

    message += f"<b><u>Output</u></b>\n"

    if out.getvalue().strip() == "":
        message += f"<code>== No output ==</code>\n\n"
    else:
        message += f"<code>{html.escape(out.getvalue())}</code>\n\n"

    if err.getvalue().strip() != "":
        message += f"<b><u>Error</u></b>\n<code>{html.escape(err.getvalue())}</code>\n"

    await send.edit(message, parse_mode=ParseMode.HTML)

    # make sure redirect output to terminal
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
