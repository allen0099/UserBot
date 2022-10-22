import asyncio
from datetime import datetime, timedelta

from pyrogram.errors import FloodWait

import bot
from core.settings import TIMEZONE


class KickChatMember:
    async def kick_chat_member(
        self: "bot.Bot", chat_id: int | str, user_id: int | str
    ) -> bool:
        ban_time: datetime = datetime.now(TIMEZONE)
        ban_time += timedelta(minutes=1)

        try:
            await self.ban_chat_member(chat_id, user_id, ban_time)

        except FloodWait as error:
            await asyncio.sleep(error.value)

        return True
