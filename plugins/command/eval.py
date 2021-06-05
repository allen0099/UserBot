import ast
import html
import logging
import re
import sys
import traceback
from _ast import AST, Module
from io import StringIO
from typing import Union

from pyrogram import Client, filters
from pyrogram.types import Message

log: logging.Logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/60934327
@Client.on_message(filters.command("eval", prefixes=".") & filters.me)
async def api(cli: Client, msg: Message) -> None:
    out: StringIO = StringIO()
    sys.stdout = out
    err: StringIO = StringIO()
    sys.stderr = err

    parsed_fn: Union[AST, Module] = ast.parse(f"async def __s(cli: Client, msg: Message): pass")

    message: str = f"<b><u>Expression</u></b>\n"
    send: Message = await msg.reply(message, parse_mode="html")

    cmd: str = re.findall(r"(?s)(?<=\.eval ).*", msg.text)[0]

    log.info(f"{msg.from_user.id} try to execute\n{cmd}")

    message += f"<code>{html.escape(cmd)}</code>\n\n"
    await send.edit(message, parse_mode="html")

    # noinspection PyBroadException
    try:
        parsed_stmts: Union[AST, Module] = ast.parse(cmd)

        for _ in parsed_stmts.body:
            ast.increment_lineno(_)

        parsed_fn.body[0].body = parsed_stmts.body

        exec(compile(parsed_fn, filename="<ast>", mode="exec"), None)
        await eval("__s(cli, msg)", None)
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
