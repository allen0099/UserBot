import html
import inspect
from typing import Any

from pyrogram import enums, errors, raw, types
from pyrogram.utils import get_channel_id

from bot import Bot
from bot.enums import EmojiList
from bot.functions import capitalize
from bot.functions.links import (
    get_linked_chat_link,
    get_pinned_message_link,
    get_sticker_pack_link,
    get_uid_mention_link,
)


async def parse_res_reason(reasons: list[raw.types.RestrictionReason]) -> str:
    message: str = ""

    if reasons:
        message = f"\n<b><u>Restriction reason(s)</u></b>\n"

        for reason in reasons:
            message += (
                f"<code>-> {reason.platform} - {reason.reason}</code>\n"
                f"<code>   </code>{reason.text}\n"
            )

    return message


async def parse_rights(right: raw.types.ChatAdminRights) -> str:
    tests: list[tuple[str, Any]] = [
        _
        for _ in inspect.getmembers(right)
        if not inspect.ismethod(_[1])
        and not inspect.isfunction(_[1])
        and not _[0].startswith("_")
        and _[0] not in ["ID", "QUALNAME"]
    ]
    message: str = f""

    for test in tests:
        message += f"{getattr(EmojiList, test[0]) if test[1] else EmojiList.DENY}"

    return message


async def parse_permission(rights: raw.types.ChatBannedRights) -> str:
    tests: list[tuple[str, Any]] = [
        _
        for _ in inspect.getmembers(rights)
        if not inspect.ismethod(_[1])
        and not inspect.isfunction(_[1])
        and not _[0].startswith("_")
        and _[0] not in ["ID", "QUALNAME"] + ["until_date"]
    ]

    message: str = f"\n<u><b>Chat Permission</b></u>\n"

    for test in tests:
        message += f"{EmojiList.FALSE if test[1] else EmojiList.TRUE} <b>{capitalize(test[0])}</b>\n"

    return message


async def parse_admin(
    admins: list[raw.types.ChannelParticipantAdmin], users: dict[int, raw.types.User]
) -> str:
    message: str = f""

    for admin in admins:
        message += await parse_rights(admin.admin_rights)

        if users[admin.user_id].bot:
            message += (
                f"({EmojiList.BOT})"
                f"({EmojiList.BOT_EYES if users[admin.user_id].bot_chat_history else EmojiList.BOT_CLOSE_EYES})"
            )

        message += (
            f"<code>[{html.escape(admin.rank or '')}]</code> "
            f"{get_uid_mention_link(users[admin.user_id])}\n"
        )

    return message.strip()


async def parse_channel_admins(cli: Bot, channel: raw.types.Channel) -> str:
    peer = await cli.resolve_peer(get_channel_id(channel.id))

    channel_participants: raw.types.channels.ChannelParticipants = await cli.invoke(
        raw.functions.channels.GetParticipants(
            channel=peer,
            filter=raw.types.ChannelParticipantsAdmins(),
            offset=0,
            limit=200,
            hash=0,
        ),
        sleep_threshold=60,
    )

    participants: list[raw.base.ChannelParticipant] = channel_participants.participants
    users: dict[int, raw.types.User] = {i.id: i for i in channel_participants.users}

    creator: list[raw.types.ChannelParticipantCreator] = [
        _ for _ in participants if isinstance(_, raw.types.ChannelParticipantCreator)
    ]

    if creator:
        creator: raw.types.ChannelParticipantCreator = creator[0]

        user_creator: raw.types.User = users[creator.user_id]

        message: str = (
            f"群主：<code>[{html.escape(creator.rank or '')}]</code> "
            f"{get_uid_mention_link(user_creator)}\n"
        )

    else:
        message: str = f"群主：<code>匿名的群主</code>\n"

    admins: list[raw.types.ChannelParticipantAdmin] = [
        _
        for _ in participants
        if isinstance(_, raw.types.ChannelParticipantAdmin) and not users[_.user_id].bot
    ]
    bots: list[raw.types.ChannelParticipantAdmin] = [
        _ for _ in participants if users[_.user_id].bot
    ]

    admins.sort(key=lambda x: x.user_id)
    bots.sort(key=lambda x: x.user_id)

    message += (
        f"{await parse_admin(admins, users)}\n{await parse_admin(bots, users)}\n"
    ).strip()

    return message


async def parse_user(
    api_user: raw.types.User, full_user: raw.types.UserFull, user: types.User
) -> str:
    username_holder: str = f"<b>使用者名稱：</b>@{user.username}\n" if user.username else ""
    message: str = (
        f"<b><u>User info</u></b>\n"
        f"<b>使用者 ID：</b><code>{user.id}</code>\n"
        f"<b>名字：</b>{user.mention}\n"
        f"<b>姓氏：</b>{html.escape(user.last_name or '')}\n"
        f"{username_holder}"
        f"<b>共同群組：</b>{full_user.common_chats_count}\n"
    )

    if full_user.about:
        message += f"<b>個人簡介：</b>\n<code>{html.escape(full_user.about or '')}</code>\n"

    message += "\n<b><u>Properties</u></b>\n"

    tests: list[tuple[str, Any]] = [
        _
        for _ in inspect.getmembers(user)
        if _[0].startswith("is_")
        and not _[0].endswith("self")
        and not _[0].endswith("contact")
    ]

    for test in tests:
        message += f"{EmojiList.TRUE if test[1] else EmojiList.FALSE} <b>{capitalize(test[0][3:])}</b>\n"

    message += "\n<b><u>Call settings</u></b>\n"

    full_user_tests: list[str] = [
        "phone_calls_available",
        "phone_calls_private",
        "video_calls_available",
        "voice_messages_forbidden",
    ]

    for test in full_user_tests:
        message += f"{EmojiList.TRUE if getattr(full_user, test) else EmojiList.FALSE} <b>{capitalize(test)}</b>\n"

    message += await parse_res_reason(api_user.restriction_reason)

    return message


async def parse_bot(api_user: raw.types.User, full_user: raw.types.UserFull) -> str:
    if api_user.bot:
        return (
            f"\n<b><u>Bot info</u></b>\n"
            f"{EmojiList.TRUE if api_user.bot_chat_history else EmojiList.FALSE} 允許閱讀訊息\n"
            f"{EmojiList.FALSE if api_user.bot_nochats else EmojiList.TRUE} 允許加入群組\n"
            f"{EmojiList.TRUE if api_user.bot_inline_geo else EmojiList.FALSE} 允許內聯模式要求位置權限\n"
            f"{EmojiList.TRUE if api_user.bot_attach_menu else EmojiList.FALSE} 允許加入選項 (Attach Menu)\n"
            f"<b>機器人內聯提示：</b>"
            f"<code>{api_user.bot_inline_placeholder or ''}</code>\n"
            f"<b>群組建議權限：</b>\n"
            f"<code>{await parse_rights(full_user.bot_group_admin_rights)}</code>\n"
            f"<b>頻道建議權限：</b>\n"
            f"<code>{await parse_rights(full_user.bot_broadcast_admin_rights)}</code>\n"
            f"<b>機器人簡介版本：</b><code>{api_user.bot_info_version}</code>\n"
            f"<b>機器人簡介：</b>\n"
            f"<code>{full_user.bot_info.description if full_user.bot_info else None}</code>\n"
        )
    return ""


async def parse_channel(
    cli: Bot,
    api_channel: raw.types.Channel,
    full_channel: raw.types.ChannelFull,
    channel: types.Chat,
) -> str:
    try:
        admins = await cli.get_chat_admins(channel.id)

    except errors.ChatAdminRequired:
        admins: list = []

    holder: str = "頻道" if api_channel.broadcast else "群組"

    username_holder: str = (
        f"<b>{holder}名稱：</b>@{channel.username}\n" if channel.username else ""
    )
    message: str = (
        f"<b><u>Channel info</u></b>\n"
        f"<b>{holder} ID：</b><code>{get_channel_id(api_channel.id)}</code>\n"
        f"<b>類型：</b><code>{channel.type.name.capitalize()}</code>\n"
        f"<b>{holder}標題：</b><code>{html.escape(channel.title)}</code>\n"
        f"{username_holder}"
        f"<b>管理員數量：</b><code>{len(admins)}</code>\n"
        f"<b>成員數量：</b><code>{full_channel.participants_count}</code>\n"
    )

    if full_channel.about:
        message += (
            f"<b>{holder}描述</b>\n<code>{html.escape(full_channel.about or '')}</code>\n"
        )

    if channel.pinned_message:
        message += f"{get_pinned_message_link(channel.pinned_message)}\n"

    if channel.linked_chat:
        message += f"{get_linked_chat_link(channel.linked_chat)}\n"

    sticker: raw.types.StickerSet = full_channel.stickerset
    if sticker:
        message += f"<b>群組貼圖：</b>{get_sticker_pack_link(sticker)}\n"

    message += "\n<b><u>Properties</u></b>\n"

    tests: list[tuple[str, Any]] = [
        _
        for _ in inspect.getmembers(channel)
        if _[0].startswith("is_") and not _[0].endswith("creator")
    ] + [("is_signatures", api_channel.signatures)]

    tests.sort(key=lambda x: x[0])

    for test in tests:
        message += f"{EmojiList.TRUE if test[1] else EmojiList.FALSE} <b>{capitalize(test[0][3:])}</b>\n"

    message += await parse_res_reason(api_channel.restriction_reason)

    if channel.type != enums.ChatType.CHANNEL:
        message += (
            "\n<b><u>Admins</u></b>\n"
            f"{await parse_channel_admins(cli, api_channel)}\n"
            f"{await parse_permission(api_channel.default_banned_rights)}\n"
        )

    return message
