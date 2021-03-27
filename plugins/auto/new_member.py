import logging
import os

from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.types import Chat, Message, User

from bot.util import get_common_chats
from database.models import Name
from database.models.Name import CATEGORY
from main import user_bot

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.new_chat_members & ~ filters.me)
async def add_member_report(cli: Client, msg: Message) -> None:
    me = user_bot.me
    new_users: dict[int, User] = {i.id: i for i in msg.new_chat_members}

    if msg.from_user.id in new_users.keys():
        # Others joined the group
        await check_name(cli, msg)
        return

    # Others add me
    if me.id in new_users.keys():
        inviter_commons: list[Chat] = await get_common_chats(cli, msg.from_user.id)
        if len(inviter_commons) <= 3:
            log.debug(f"What happened, I should leave {msg.chat.title}({msg.chat.id}) and report now.")
            if await cli.send(functions.messages.ReportSpam(peer=await cli.resolve_peer(msg.chat.id))):
                await cli.send_message(os.getenv("LOG_CHANNEL"),
                                       f"#auto #reportspam #leave {msg.chat.title}({msg.chat.id})")
                await cli.leave_chat(msg.chat.id)
                return
            await cli.send_message(os.getenv("LOG_CHANNEL"), f"#auto #failed {msg.chat.title}({msg.chat.id})")
            return

    # Others add another one
    def get_str_mbs(x: list[User]) -> list[str]:
        return [f"{_.first_name}{' ' + _.last_name if _.last_name else ''}({_.id})" for _ in x]

    log.debug(f"{msg.from_user.id} invited {get_str_mbs(msg.new_chat_members)} into {msg.chat.title}({msg.chat.id})")


async def check_name(cli: Client, msg: Message):
    full_name: str = msg.from_user.first_name + (f" {msg.from_user.last_name}" if msg.from_user.last_name else "")
    log.debug(f"User {full_name}({msg.from_user.id}) joined the group {msg.chat.title}({msg.chat.id}), checking name.")

    for _ in Name.get_dict(CATEGORY.PREFIX):
        if msg.from_user.first_name.startswith(_.match) and len(msg.from_user.first_name) in (3, 4):
            await cli.send_message(os.getenv("LOG_CHANNEL"),
                                   f"#auto #ban #name #prefix <code>{full_name}</code>\n"
                                   f"Uid {msg.from_user.id}\n"
                                   f"Due to name_prefix: {_.match}\n"
                                   f"From {msg.chat.title}({msg.chat.id})")
            return

    for _ in Name.get_dict(CATEGORY.CONTAIN):
        if _.match in full_name:
            await cli.send_message(os.getenv("LOG_CHANNEL"),
                                   f"#auto #ban #name #contain <code>{full_name}</code>\n"
                                   f"Uid {msg.from_user.id}\n"
                                   f"Due to contain: {_.match}\n"
                                   f"From {msg.chat.title}({msg.chat.id})")
            return
