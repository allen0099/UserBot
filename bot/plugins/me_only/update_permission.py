import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.functions import msg_auto_clean
from bot.plugins import COMMAND_PREFIXES
from core.log import event_logger, main_logger
from database.models.privilege import Privilege

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("update", prefixes=COMMAND_PREFIXES)
    & filters.group
    & filters.me
    & ~filters.forwarded
)
async def update(cli: Client, msg: Message) -> None:
    await msg.delete()

    if len(msg.command) > 1:
        match msg.command[1]:
            case "noset":
                privilege: Privilege = Privilege.get(msg.chat.id)

                privilege.clear()
                privilege.write()

                await msg_auto_clean(
                    await cli.send_message(
                        msg.chat.id,
                        f"已清空此群組權限設定",
                    )
                )

            case _:
                await msg_auto_clean(
                    await cli.send_message(
                        msg.chat.id,
                        f"操作失敗，未知的參數\n可用參數：<code>noset</code>",
                    )
                )
        return

    privilege: Privilege = Privilege.get(msg.chat.id)

    if privilege:
        await privilege.create_or_update(msg)

        await msg_auto_clean(await cli.send_message(msg.chat.id, "已更新此群組的權限設定"))
