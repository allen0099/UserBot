import logging

import bot
from core.log import main_logger

log: logging.Logger = main_logger(__name__)


class DeleteRangeMessages:
    async def delete_range_messages(
        self: "bot.Bot", chat_id: int, start: int, stop: int
    ) -> None:
        if start > stop:
            await self.send_message(chat_id, "<b><i>Start should before stop</b></i>")
            return

        while (stop - start) > 100:
            await self.delete_messages(chat_id, [_ for _ in range(start, start + 100)])
            start += 100

        await self.delete_messages(chat_id, [_ for _ in range(start, stop + 1)])
