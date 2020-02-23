import logging

from pyrogram import Client, Message, Filters

log: logging.Logger = logging.getLogger(__name__)


# TODO: rewrite this
@Client.on_message(Filters.command("everyone", prefixes="@") & Filters.group & Filters.me)
def mention_everyone(cli: Client, msg: Message) -> None:
    cli.delete_messages(msg.chat.id, [msg.message_id])

    members = cli.iter_chat_members(msg.chat.id)
    string = ""
    for i in members:
        string += f"<a href='tg://user?id={i.user.id}'>" + "\u2060" + "</a>"
    string += "@everyone"
    cli.send_message(msg.chat.id, string, parse_mode="HTML",
                     disable_notification=False)


@Client.on_message(Filters.command("admin", "@") & Filters.group & Filters.me)
def mention_admins(cli: Client, msg: Message) -> None:
    cli.delete_messages(msg.chat.id, [msg.message_id])

    admins = cli.iter_chat_members(msg.chat.id, filter="Administrators")
    string = ""
    for i in admins:
        string += f"<a href='tg://user?id={i.user.id}'>" + "\u2060" + "</a>"
    string += "@admin"
    cli.send_message(msg.chat.id, string, parse_mode="HTML",
                     disable_notification=False)
