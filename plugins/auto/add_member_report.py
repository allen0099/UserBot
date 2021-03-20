import logging
import os

from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.types import Chat, Message, User

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.new_chat_members & ~ filters.me)
async def add_member_report(cli: Client, msg: Message) -> None:
    me: User = await cli.get_me()
    new_users: dict[int, User] = {i.id: i for i in msg.new_chat_members}

    if msg.from_user.id in new_users.keys():
        log.debug(f"User {msg.from_user.id} joined the group {msg.chat.title}({msg.chat.id}) via any, do nothing.")
        return

    inviter_common_groups: list[Chat] = await cli.get_common_chats(msg.from_user.id)

    if me.id in new_users.keys() and len(inviter_common_groups) <= 3:
        log.debug(f"What happened, I should leave {msg.chat.id} and report now.")
        if await cli.send(functions.messages.ReportSpam(peer=await cli.resolve_peer(msg.chat.id))):
            await cli.send_message(os.getenv("log_channel"), f"#auto #leave #id{msg.chat.id}")
            # await cli.leave_chat(msg.chat.id)
        await cli.send_message(os.getenv("LOG_CHANNEL"), f"#id{msg.chat.id} #test #not_report")
        await cli.send_message(os.getenv("LOG_CHANNEL"), f"<code>{msg}</code>")
