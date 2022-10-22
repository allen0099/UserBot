from html import escape

from pyrogram import types
from pyrogram.errors import UserNotParticipant

import bot
from bot.functions import msg_auto_clean


class GetChatMemberFromMessage:
    async def get_chat_member_from_message(
        self: "bot.Bot", message: types.Message, user_id: int | str
    ) -> types.ChatMember:
        try:
            return await self.get_chat_member(message.chat.id, user_id)

        except UserNotParticipant:
            await msg_auto_clean(
                await message.reply_text(f"<b>錯誤：使用者已經不在 {escape(message.chat.title)} 中！</b>")
            )
