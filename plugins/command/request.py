import html
import logging
import re
from typing import Union

from pyrogram import Client, filters, utils
from pyrogram.raw import base, functions, types
from pyrogram.raw.types import ChannelParticipantAdmin, ChannelParticipantCreator, ChannelParticipantsAdmins, \
    ChatAdminRights, RestrictionReason, StickerSet
from pyrogram.raw.types.channels import ChannelParticipants
from pyrogram.types import Message

from bot.functions import get_full
from bot.types import EMOJI
from database.models import Channel, ChatBannedRights, User

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("req", prefixes="$") & filters.me & ~ filters.forwarded)
async def request(cli: Client, msg: Message) -> None:
    log.debug(f"{msg.from_user.id} issued command request")
    log.debug(f" -> text: {msg.text}")

    try:
        peer_id: str = re.search(re.compile(r"(?<=@)?\w{5,}$|^[+-]?\d+$|(?:me|self)$"), msg.command[1])[0]
        log.debug(f"Peer id: {peer_id}")
    except (IndexError, TypeError):
        await cli.send_message("me", "Usage: <code>$req &lt;uid|username&gt;</code>")
        return
    else:
        data: Union[User, Channel] = await get_full(cli, peer_id)
        if isinstance(data, User):
            await msg.reply_text(await parse_user(data))
            return
        elif isinstance(data, Channel):
            await msg.reply_text(await parse_channel(cli, data))
            return
        else:
            await msg.reply_text("Not yet support")
            return


async def parse_user(user: User) -> str:
    message: str = f"<b>UID</b>: <code>{user.uid}</code>\n" \
                   f"<b>User data center</b>: <code>{user.dc_id}</code>\n" \
                   f"<b>First Name</b>: <a href='tg://user?id={user.id}'>{html.escape(user.first_name)}</a>\n" \
                   f"<b>Last Name</b>: {html.escape(user.last_name if user.last_name else EMOJI.empty)}\n" \
                   f"<b>Username</b>: @{user.username}\n" \
                   f"<b>Bio</b>: \n" \
                   f"<code>{html.escape(user.about)}</code>\n" \
                   f"<b>Bot</b>: {EMOJI.true if user.bot else EMOJI.false}\n" \
                   f"<b>Deleted</b>: {EMOJI.true if user.deleted else EMOJI.false}\n" \
                   f"<b>Verified</b>: {EMOJI.true if user.verified else EMOJI.false}\n" \
                   f"<b>Scam</b>: {EMOJI.true if user.scam else EMOJI.false}\n" \
                   f"<b>Support</b>: {EMOJI.true if user.support else EMOJI.false}\n" \
                   f"<b>Restricted</b>: {EMOJI.true if user.restricted else EMOJI.false}\n" \
                   f"<b>Phone call available</b>: {EMOJI.true if user.phone_calls_available else EMOJI.false}\n" \
                   f"<b>Phone call in privacy setting</b>: " \
                   f"{EMOJI.true if user.phone_calls_private else EMOJI.false}\n" \
                   f"<b>Video call</b>: {EMOJI.true if user.video_calls_available else EMOJI.false}\n" \
                   f"<b>Groups in common</b>: {user.common_chats_count}\n"
    return message


async def parse_channel(cli: Client, channel: Channel) -> str:
    message: str = f"<b>Chat ID</b>: <code>{utils.get_channel_id(channel.cid)}</code>\n" \
                   f"<b>Chat Type</b>: <code>{'Channel' if channel.broadcast else 'Supergroup'}</code>\n" \
                   f"<b>Chat Title</b>: <code>{html.escape(channel.title)}</code>\n" \
                   f"<b>Chat Username</b>: @{channel.username}\n" \
                   f"<b>Description</b>:\n" \
                   f"<code>{html.escape(channel.about)}</code>\n"

    message += f"<b>Administrator counts</b>: <code>{channel.admins_count}</code>\n" \
               f"<b>Member counts</b>: <code>{channel.participants_count}</code>\n" \
               f"<b>Verified</b>: {EMOJI.true if channel.verified else EMOJI.false}\n" \
               f"<b>Scam</b>: {EMOJI.true if channel.scam else EMOJI.false}\n" \
               f"<b>Signatures</b>: {EMOJI.true if channel.signatures else EMOJI.false}\n" \
               f"<b>Restricted</b>: {EMOJI.true if channel.restricted else EMOJI.false}\n"

    import pyrogram
    log.debug(f"Call for use: {pyrogram.__version__}")

    restriction_reason: list[RestrictionReason] = eval(channel.restriction_reason)

    if restriction_reason:
        message += f"<b>Restriction reason(s)</b>:\n"
        for reason in restriction_reason:
            message += f"-> <code>{reason.platform} - {reason.reason}</code>\n" \
                       f"   {reason.text}\n"

    if channel.pinned_msg_id:
        message += f"🔗 <a href='https://t.me/c/{channel.cid}/{channel.pinned_msg_id}'>Pinned message</a>\n"
    if channel.linked_chat_id:
        message += f"🔗 <a href='https://t.me/c/{channel.linked_chat_id}/999999999'>Linked Chat</a>\n"

    sticker: StickerSet = eval(channel.sticker_link)
    if sticker:
        message += f"<b>Group Stickers</b>: <a href='https://t.me/addstickers/{sticker.short_name}'>" \
                   f"{html.escape(sticker.title)}</a>\n"
    if not channel.broadcast:
        message += await parse_permission(channel.default_banned_rights)
        message += await parse_channel_admins(cli, channel)

    return message


async def parse_permission(rights: ChatBannedRights) -> str:
    message: str = f"\n<u><b>Chat Permission</b></u>:\n" \
                   f"<b>Send message</b>: {EMOJI.false if rights.send_messages else EMOJI.true}\n" \
                   f"<b>Send media</b>: {EMOJI.false if rights.send_media else EMOJI.true}\n" \
                   f"<b>Send stickers</b>: {EMOJI.false if rights.send_stickers else EMOJI.true}\n" \
                   f"<b>Send gifs</b>: {EMOJI.false if rights.send_gifs else EMOJI.true}\n" \
                   f"<b>Send games</b>: {EMOJI.false if rights.send_games else EMOJI.true}\n" \
                   f"<b>Send inline</b>: {EMOJI.false if rights.send_inline else EMOJI.true}\n" \
                   f"<b>Embed links</b>: {EMOJI.false if rights.embed_links else EMOJI.true}\n" \
                   f"<b>Send polls</b>: {EMOJI.false if rights.send_polls else EMOJI.true}\n" \
                   f"<b>Change info</b>: {EMOJI.false if rights.change_info else EMOJI.true}\n" \
                   f"<b>Invite users</b>: {EMOJI.false if rights.invite_users else EMOJI.true}\n" \
                   f"<b>Pin messages</b>: {EMOJI.false if rights.pin_messages else EMOJI.true}\n"
    return message


async def parse_channel_admins(cli: Client, channel: Channel) -> str:
    peer = await cli.resolve_peer(utils.get_channel_id(channel.cid))

    channel_participants: ChannelParticipants = await cli.send(
        functions.channels.GetParticipants(
            channel=peer,
            filter=ChannelParticipantsAdmins(),
            offset=0,
            limit=200,
            hash=0
        ),
        sleep_threshold=60
    )

    participants: list[base.ChannelParticipant] = channel_participants.participants
    users: dict[int, types.User] = {i.id: i for i in channel_participants.users}

    creator: ChannelParticipantCreator = [_ for _ in participants if isinstance(_, ChannelParticipantCreator)][0]
    admins: list[ChannelParticipantAdmin] = [_ for _ in participants if
                                             isinstance(_, ChannelParticipantAdmin) and not users[_.user_id].bot]
    bots: list[ChannelParticipantAdmin] = [_ for _ in participants if users[_.user_id].bot]

    admins.sort(key=lambda x: x.user_id)
    bots.sort(key=lambda x: x.user_id)

    user_creator: types.User = users[creator.user_id]
    message: str = f"\n<u><b>Administrators</b></u>:\n" \
                   f"Creator: <code>[{html.escape(creator.rank) if creator.rank else EMOJI.empty}]</code> " \
                   f"<a href='tg://user?id={creator.user_id}'>" \
                   f"{html.escape(user_creator.first_name) if user_creator.first_name else EMOJI.empty} " \
                   f"{html.escape(user_creator.last_name) if user_creator.last_name else EMOJI.empty}</a>\n"

    message += parse_admin(admins, users)
    message += parse_admin(bots, users)

    return message


def parse_rights(right: ChatAdminRights) -> str:
    ret: str = f"{EMOJI.info if right.change_info else EMOJI.deny}" \
               f"{EMOJI.delete if right.delete_messages else EMOJI.deny}" \
               f"{EMOJI.ban if right.ban_users else EMOJI.deny}" \
               f"{EMOJI.add_member if right.invite_users else EMOJI.deny}" \
               f"{EMOJI.pin if right.pin_messages else EMOJI.deny}" \
               f"{EMOJI.voice if right.manage_call else EMOJI.deny}" \
               f"{EMOJI.add_admin if right.add_admins else EMOJI.deny}"
    return ret


def parse_admin(admins: list[ChannelParticipantAdmin], users: dict[int, types.User]) -> str:
    ret: str = f""
    for _ in admins:
        ret += parse_rights(_.admin_rights)

        if users[_.user_id].bot:
            ret += f"({EMOJI.bot})"
            ret += f"({EMOJI.bot_eyes if users[_.user_id].bot_chat_history else EMOJI.bot_close_eyes})"
        ret += f"<code>[{html.escape(_.rank) if _.rank else EMOJI.empty}]</code> " \
               f"<a href='tg://user?id={_.user_id}'>" \
               f"{html.escape(users[_.user_id].first_name) if users[_.user_id].first_name else EMOJI.empty} " \
               f"{html.escape(users[_.user_id].last_name) if users[_.user_id].last_name else EMOJI.empty}</a>\n"

    return ret
