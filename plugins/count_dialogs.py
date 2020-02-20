import logging

from pyrogram import Client, Filters, Message

log = logging.getLogger(__name__)


@Client.on_message(Filters.command("countmsg", prefixes="$") & Filters.me)
def count_dialogs(cli: Client, msg: Message) -> None:
    # TODO: make this more quickly
    cli.delete_messages(msg.chat.id, [msg.message_id])

    r = cli.iter_dialogs()
    total = 0
    group = 0
    super_group = 0
    channel = 0
    private = 0
    bot = 0
    sent = cli.send_message(msg.chat.id, "計算中，將會花費一點時間，請稍等")
    for _ in r:
        _dialog_type = _.chat.type
        total += 1
        if _dialog_type == "supergroup":
            super_group += 1
        elif _dialog_type == "group":
            group += 1
        elif _dialog_type == "channel":
            channel += 1
        elif _dialog_type == "private":
            private += 1
        elif _dialog_type == "bot":
            bot += 1
        else:
            """TODO"""
            pass
    string = f"Total: {total}\n" \
             f"Groups: {group}\n" \
             f"Super groups: {super_group}\n" \
             f"Channel: {channel}\n" \
             f"Private: {private}\n" \
             f"Bot: {bot}\n"
    cli.edit_message_text(sent.chat.id, sent.message_id, string)
