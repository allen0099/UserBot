import html
import logging
import time

import pyrogram
from pyrogram import Client, Message, Filters
from pyrogram.api.functions import channels

from bot.plugins import COMMAND_PREFIX
from bot.plugins.auth.command import LOG_CHANNEL
from models import Users

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.user(Users.get()) &
                   Filters.command("bang", prefixes=COMMAND_PREFIX) &
                   Filters.group &
                   Filters.reply)
def bang(cli: Client, msg: Message) -> None:
    chat: pyrogram.Chat = msg.chat
    execute_user: pyrogram.User = msg.from_user

    reply_message: pyrogram.Message = msg.reply_to_message
    ban_user: pyrogram.User = msg.reply_to_message.from_user

    permission: pyrogram.ChatMember = cli.get_chat_member(msg.chat.id, cli.get_me().id)

    if permission.status == "administrator" and \
            permission.can_delete_messages is True and \
            permission.can_restrict_members is True:

        if not reply_message.service:
            cli.forward_messages(LOG_CHANNEL, chat.id, reply_message.message_id)
        else:
            """Service means user join"""
            string: str = f"===Joined Message===\n" \
                          f"From chat: <code>{html.escape(chat.title)}({chat.id})</code>\n" \
                          f"User join: <a href='tg://user?id={ban_user.id}'>{html.escape(str(ban_user.first_name))}</a>" \
                          f"({ban_user.id})"
            cli.send_message(LOG_CHANNEL, string)

        string: str = f"+++Banned Info+++\n" \
                      f"From chat: <code>{html.escape(chat.title)}({chat.id})</code>\n" \
                      f"Execute user: <a href='tg://user?id={execute_user.id}'>{html.escape(str(execute_user.first_name))}</a>" \
                      f"({execute_user.id})\n" \
                      f"Execute time: {time.asctime()}\n" \
                      f"Banned user: <a href='tg://user?id={ban_user.id}'>{html.escape(str(ban_user.first_name))}</a>" \
                      f"({ban_user.id})"
        cli.send_message(LOG_CHANNEL, string)
    # delete all message first
    cli.send(
        channels.DeleteUserHistory(
            channel=cli.resolve_peer(chat.id),
            user_id=cli.resolve_peer(ban_user.id)
        )
    )
    # ban later
    cli.kick_chat_member(chat.id, ban_user.id)

    cli.delete_messages(chat.id, [msg.message_id, reply_message.message_id])
