import html
import logging
import re
import sys
import traceback
from io import StringIO

from pyrogram import Client, Filters, Message

log = logging.getLogger(__name__)


@Client.on_message(Filters.command("eval", prefixes=".") & Filters.me)
def api(cli: Client, msg: Message) -> None:
    sys.stdout = out = StringIO()
    sys.stderr = err = StringIO()
    init_str = f"<b>Expression</b>:\n"
    send = cli.send_message(msg.chat.id, init_str, parse_mode="html")
    regex = r"(?<=\.eval ).*"
    para = re.findall(regex, msg.text, re.MULTILINE | re.DOTALL)[0]

    # noinspection PyBroadException
    try:
        c = compile(para, 'abc', 'single')
        init_str += f"<code>{html.escape(para)}</code>\n\n"
        send.edit(init_str)
        eval(c)
    except Exception:
        lines = traceback.format_exc().splitlines()
        print(lines[-1], file=err)
    if out.getvalue() != "":
        init_str += f"<b>Output</b>:\n" \
                    f"<code>{html.escape(out.getvalue())[0:-1]}</code>\n\n"
        send.edit(init_str)
    if err.getvalue() != "":
        init_str += f"<b>Error</b>:\n" \
                    f"<code>{html.escape(err.getvalue())[0:-1]}</code>\n"
        send.edit(init_str)
    # make sure redirect output to terminal
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
