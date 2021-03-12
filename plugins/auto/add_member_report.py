import logging
from typing import Optional

from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.types import Chat, Message, User

from bot.functions import get_configs
from bot.types.Config import Config

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.new_chat_members)
async def add_member_report(cli: Client, msg: Message) -> Optional[Message]:
    me: User = await cli.get_me()
    if msg.from_user.id == me.id:
        return

    common_chats: list[Chat] = await cli.get_common_chats(msg.from_user.id)
    configs: Config = get_configs()

    if len(common_chats) <= 3:
        if await cli.send(functions.messages.ReportSpam(peer=await cli.resolve_peer(msg.chat.id))):
            await cli.leave_chat(msg.chat.id)
            return await cli.send_message(configs.log_channel, f"#auto #leave #id{msg.chat.id}")
        return await cli.send_message(configs.log_channel, f"#auto #leave #id{msg.chat.id} #failed")
