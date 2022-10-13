import logging
from html import escape

from pyrogram import raw, types
from pyrogram.enums import ParseMode
from pyrogram.types.user_and_chats.user import Link
from pyrogram.utils import get_channel_id

from core import main_logger

log: logging.Logger = main_logger(__name__)


def get_chat_link(chat: types.Chat) -> Link:
    return Link(
        f"https://t.me/{chat.username}"
        if chat.username
        else f"https://t.me/c/{get_channel_id(chat.id)}/1",
        escape(chat.title),
        chat._client.parse_mode,
    )


def get_message_link(chat: types.Chat, message_id: int) -> Link:
    return Link(
        f"https://t.me/{chat.username}/{message_id}"
        if chat.username
        else f"https://t.me/c/{get_channel_id(chat.id)}/{message_id}",
        escape(chat.title),
        chat._client.parse_mode,
    )


def get_uid_mention_link(user: raw.types.User) -> Link:
    return Link(
        f"tg://user?id={user.id}",
        f"{user.id}",
        ParseMode.DEFAULT,
    )


def get_sticker_pack_link(sticker: raw.types.StickerSet) -> Link:
    return Link(
        f"https://t.me/addstickers/{sticker.short_name}",
        escape(sticker.title),
        ParseMode.DEFAULT,
    )


def get_pinned_message_link(message: types.Message) -> Link:
    return Link(
        message.link,
        "🔗 Pinned Message",
        message.chat._client.parse_mode,
    )


def get_linked_chat_link(chat: types.Chat) -> Link:
    return Link(
        f"https://t.me/{chat.username}"
        if chat.username
        else f"https://t.me/c/{get_channel_id(chat.id)}/999999999",
        "🔗 Linked Chat",
        chat._client.parse_mode,
    )
