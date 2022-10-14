from pyrogram import types
from pyrogram.enums import ChatMembersFilter

import bot


class GetChatAdmins:
    async def get_chat_admins(
        self: "bot.Bot",
        chat_id: int | str,
        query: str = "",
        limit: int = 0,
    ) -> list[types.ChatMember]:
        admins: list[types.ChatMember] = [
            user
            async for user in self.get_chat_members(
                chat_id, query, limit, filter=ChatMembersFilter.ADMINISTRATORS
            )
        ]

        return admins
