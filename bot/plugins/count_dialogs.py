import logging
from typing import Generator

import pyrogram
from pyrogram import Client, Filters, Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("countmsg", prefixes="$") & Filters.me)
def count_dialogs(cli: Client, msg: Message) -> None:
    cli.delete_messages(msg.chat.id, [msg.message_id])

    r: Generator["pyrogram.Dialog"] = cli.iter_dialogs()

    count: dict = {
        "total": 0,
        "group": 0,
        "supergroup": 0,
        "channel": 0,
        "private": 0,
        "bot": 0
    }

    sent: Message = cli.send_message(msg.chat.id, "計算中，將會花費一點時間，請稍等")
    for _ in r:
        count["total"] += 1
        _dialog_type: str = _.chat.type
        if _dialog_type == "supergroup":
            count["supergroup"] += 1
        elif _dialog_type == "group":
            if _.top_message.migrate_to_chat_id is not None:
                count["group"] += 1
        elif _dialog_type == "channel":
            count["channel"] += 1
        elif _dialog_type == "private":
            count["private"] += 1
        elif _dialog_type == "bot":
            count["bot"] += 1
    result: str = f"Total: {count['total']}\n" \
                  f"Groups: {count['group']}\n" \
                  f"Super groups: {count['supergroup']}\n" \
                  f"Channel: {count['channel']}\n" \
                  f"Private: {count['private']}\n" \
                  f"Bot: {count['bot']}\n"
    cli.edit_message_text(sent.chat.id, sent.message_id, result)
