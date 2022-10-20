from html import escape

from pyrogram import raw, types
from pyrogram.enums import ParseMode
from pyrogram.types.user_and_chats.user import Link
from pyrogram.utils import get_channel_id


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


def get_sticker_set_link(sticker: raw.types.StickerSet) -> Link:
    return Link(
        f"tg://addstickers?set={sticker.short_name}",
        escape(sticker.title),
        ParseMode.DEFAULT,
    )


def get_pinned_message_link(message: types.Message) -> Link:
    return Link(
        message.link,
        "📌 置頂的訊息",
        message.chat._client.parse_mode,
    )


def get_linked_chat_link(chat: types.Chat) -> Link:
    return Link(
        f"https://t.me/{chat.username}"
        if chat.username
        else f"https://t.me/c/{get_channel_id(chat.id)}/999999999",
        "🔗 連結的群組",
        chat._client.parse_mode,
    )


def get_invisible_mention_link(user: types.ChatMember) -> Link:
    return Link(
        f"tg://user?id={user.user.id}",
        "\u2060",
        ParseMode.DEFAULT,
    )
