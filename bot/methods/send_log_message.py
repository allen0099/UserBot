import logging
import os
from enum import Enum

import bot
from core import main_logger

log: logging.Logger = main_logger(__name__)
LOG_CHANNEL: str = os.getenv("LOG_CHANNEL")


class LogTopics(int, Enum):
    """回復訊息主題的 message ID，會因為紀錄頻道而改變"""

    default: int = 1
    new_user: int = 2
    global_ban: int = 6
    auto: int = 14
    action: int = 16
    banned: int = 24


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
