import logging

from pyrogram import Client

log: logging.Logger = logging.getLogger(__name__)


class DeleteRangeMessages:
    async def delete_range_messages(
            self: Client,
            chat_id: int,
            start: int,
            stop: int
    ) -> None:
        if start > stop:
            await self.send_message(chat_id, "<b><i>Start should before stop</b></i>")
            return

        while (stop - start) > 100:
            await self.delete_messages(chat_id, [_ for _ in range(start, start + 100)])
            start += 100

        await self.delete_messages(chat_id, [_ for _ in range(start, stop + 1)])
