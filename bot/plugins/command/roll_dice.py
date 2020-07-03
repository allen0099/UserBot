import logging
import random

from pyrogram import Client, Message, Filters

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("random", prefixes="$") & Filters.me)
def roll_dice(cli: Client, msg: Message) -> None:
    if len(msg.command) > 2:
        tmp: list = []
        for i in msg.command[1::]:
            tmp.append(i)
        r: str = random.choice(tmp)

        msg.reply_text(r)
        log.debug(str(msg.from_user.id) + " choose " + str(r) + " from " + str(tmp))
    elif len(msg.command) == 2 and msg.command[1].isdigit():
        times: int = int(msg.command[1])
        r: int = random.randint(1, times)

        msg.reply_text(str(r))
        log.debug(str(msg.from_user.id) + " rolled " + str(r) + " in " + str(msg.command[1]))
    else:
        times: int = 6
        r: int = random.randint(1, times)

        msg.reply_text(str(r))
        log.debug(str(msg.from_user.id) + " rolled " + str(r) + " in 6")
