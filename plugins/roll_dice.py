import logging
import random

from pyrogram import Client, Message, Filters

log = logging.getLogger(__name__)


@Client.on_message(Filters.command("random", prefixes="$"))
def roll_dice(cli: Client, msg: Message) -> None:
    if len(msg.command) > 2:
        tmp = []
        for i in msg.command[1::]:
            tmp.append(i)
        r = random.choice(tmp)

        msg.reply_text(r)
        log.debug(str(msg.from_user.id) + " choose " + str(r) + " from " + str(tmp))
    elif len(msg.command) == 2 and msg.command[1].isdigit():
        times = int(msg.command[1])
        r = random.randint(1, times)

        msg.reply_text(r)
        log.debug(str(msg.from_user.id) + " rolled " + str(r) + " in " + str(msg.command[1]))
    else:
        times = 6
        r = random.randint(1, times)

        msg.reply_text(r)
        log.debug(str(msg.from_user.id) + " rolled " + str(r) + " in 6")
