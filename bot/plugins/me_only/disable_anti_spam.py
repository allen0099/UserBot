import logging

from pyrogram import Client, enums, filters, raw, types

from bot import Bot
from bot.functions import get_chat_link
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("disable_antispam", prefixes=COMMAND_PREFIXES)
    & filters.me
    & ~filters.forwarded
)
@event_log()
async def disable_anti_spam(cli: Bot, msg: types.Message) -> None:
    """
    搜尋並強制關閉 AntiSpam 功能

    Args:
        cli:
        msg:

    Returns:

    """
    await msg.edit_text("找尋有開啟 AntiSpam 的群組中...")

    total: int = await cli.get_dialogs_count()
    current: int = 0
    disabled_dialogs: list[types.Dialog] = []

    async for dialog in cli.get_dialogs():
        current += 1

        if current % 20 == 0:
            await msg.edit_text(f"找尋有開啟 AntiSpam 的群組中... ({current}/{total})")

        if dialog.chat.type == enums.ChatType.SUPERGROUP:
            channel: raw.types.ChannelFull = await cli.get_full_channel(dialog.chat.id)

            if channel.antispam:
                if await cli._set_anti_spam(dialog.chat.id, False):
                    disabled_dialogs.append(dialog)

    await msg.edit_text(
        f"找到了 {len(disabled_dialogs)} 個群組，已經關閉 AntiSpam 功能。\n"
        f"{', '.join([get_chat_link(dialog.chat) for dialog in disabled_dialogs])}",
        disable_web_page_preview=True,
    )
