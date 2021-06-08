import logging

from pyrogram import Client

log: logging.Logger = logging.getLogger(__name__)


async def delete_messages(cli: Client, chat_id: int, start: int, stop: int):
    if start > stop:
        raise ValueError("Stop should lower than start!")

    while (stop - start) > 100:
        await cli.delete_messages(chat_id, [_ for _ in range(start, start + 100)])
        start += 100

    await cli.delete_messages(chat_id, [_ for _ in range(start, stop + 1)])
