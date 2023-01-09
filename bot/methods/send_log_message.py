import os

import bot
from bot.enums import LogTopics

LOG_CHANNEL: str = os.getenv("LOG_CHANNEL")


class SendLogMessage:
    async def send_log_message(
        self: "bot.Bot",
        text: str,
        topic: LogTopics,
    ):
        await self.send_message(
            LOG_CHANNEL,
            text,
            disable_web_page_preview=True,
            reply_to_message_id=topic.value,
        )
