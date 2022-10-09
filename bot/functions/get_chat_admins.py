import logging

from pyrogram import types
from pyrogram.enums import ChatMembersFilter

import bot
from core.log import main_logger

log: logging.Logger = main_logger(__name__)


class GetChatAdmins:
    async def get_chat_admins(
        self: "bot.Bot",
        chat_id: int | str,
        query: str = "",
        limit: int = 0,
    ) -> list[types.ChatMember]:
        admins: list[types.ChatMember] = []

        async for user in self.get_chat_members(
            chat_id, query, limit, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            admins.append(user)

        return admins
