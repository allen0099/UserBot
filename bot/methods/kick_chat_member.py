import bot


class KickChatMember:
    async def kick_chat_member(
        self: "bot.Bot", chat_id: int | str, user_id: int | str
    ) -> bool:
        await self.ban_chat_member(chat_id, user_id)
        await self.unban_chat_member(chat_id, user_id)

        return True
