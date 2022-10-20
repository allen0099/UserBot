import html
import logging

from pyrogram import Client, filters, raw, types

from bot import Bot
from bot.functions import (
    get_chat_info,
    get_message_info,
    get_sticker_pack_info,
    get_user_info,
)
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("get", prefixes=COMMAND_PREFIXES)
    & filters.reply
    & filters.me
    & ~filters.forwarded
)
@event_log()
async def get(cli: Bot, msg: types.Message) -> None:
    message: str = f"<b><u>Basic Info</u></b>\n"
    replied_message: types.Message = msg.reply_to_message

    message += f"訊息 ID：<code>{replied_message.id}</code>\n"

    if replied_message.from_user:
        # Message is from a visible user
        message += get_user_info(replied_message.from_user)

    if replied_message.sender_chat:
        # Message is forwarded from a hidden user
        message += get_chat_info(replied_message.sender_chat)

    if replied_message.sticker:
        sticker_set: raw.types.StickerSet = await cli.get_sticker_set(
            replied_message.sticker.set_name
        )
        message += f"\n<b><u>Sticker Info</u></b>\n"
        message += get_sticker_pack_info(replied_message.sticker, sticker_set)

    if replied_message.forward_date:
        # Message is forwarded
        message += f"\n<b><u>Forwarded Message</u></b>\n"

        if replied_message.forward_from:
            # Message is forwarded from a visible user
            message += get_user_info(replied_message.forward_from)

        if replied_message.forward_sender_name:
            # Message is forwarded from a hidden user
            message += f"轉傳自匿名使用者：<code>{html.escape(replied_message.forward_sender_name)}</code>\n"

        if replied_message.forward_from_chat:
            # Message is forwarded from a chat
            message += get_chat_info(replied_message.forward_from_chat)

        if replied_message.forward_from_message_id:
            message += get_message_info(
                replied_message.forward_from_chat,
                replied_message.forward_from_message_id,
            )

        message += f"原始傳送時間：<code>{replied_message.forward_date}</code>\n"

        if replied_message.forward_signature:
            message += f"頻道簽名：<code>{replied_message.forward_signature}</code>\n"

    if replied_message.via_bot:
        message += f"\n<b><u>Bot Info</u></b>\n"
        message += get_user_info(replied_message.via_bot)

    await msg.reply(message, disable_web_page_preview=True)
