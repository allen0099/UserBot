import html
import logging
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import ChatMember, ChatPermissions, Message, User

from bot.filters import CustomFilters

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("mute", prefixes="!") & filters.me & CustomFilters.admin_required)
async def mute(cli: Client, msg: Message):
    await cli.delete_messages(msg.chat.id, msg.message_id)

    if msg.reply_to_message and msg.chat.type == "supergroup":
        _: User = msg.reply_to_message.from_user
        user: ChatMember = await cli.get_chat_member(msg.chat.id, _.id)
        if user.status in ("creator", "administrator"):
            await msg.reply_text("Can not restrict an admin!")
            return

        permission: ChatPermissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False,
                                                      can_send_stickers=False, can_send_animations=False,
                                                      can_send_games=False, can_use_inline_bots=False,
                                                      can_add_web_page_previews=False, can_send_polls=False,
                                                      can_change_info=False, can_invite_users=False,
                                                      can_pin_messages=False)

        try:
            until_time: datetime = get_until(msg.command[1].lower())
        except (ValueError, IndexError):
            await msg.reply_text("Input time invalid!")
            return

        await cli.restrict_chat_member(msg.chat.id, _.id, permission, int(until_time.timestamp()))
        await msg.reply_text(
            f"<a href='tg://user?id={_.id}'>{html.escape(str(_.first_name))}</a> muted until {msg.command[1].lower()}")
        return
    await msg.reply_text("Reply to a message to restrict a user")


def get_until(until: str) -> datetime:
    _: datetime = datetime.now()
    if until.endswith("d"):
        days: int = int(until.split("d")[0])
        if days < 365:
            _ += timedelta(days=days)

    if until.endswith("m"):
        minutes: int = int(until.split("m")[0])
        if minutes < 60 * 24 * 365:
            _ += timedelta(minutes=minutes)

    if _ - datetime.now() <= timedelta(seconds=58):
        raise ValueError
    return _
