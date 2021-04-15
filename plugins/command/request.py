import html
import logging
import re

from pyrogram import Client, filters, utils
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid
from pyrogram.raw import base, functions, types
from pyrogram.raw.base import ChatBannedRights, InputPeer, UserFull
from pyrogram.raw.base.messages import ChatFull
from pyrogram.raw.types import Channel, ChannelFull, ChannelParticipantAdmin, ChannelParticipantCreator, \
    ChannelParticipantsAdmins, ChatAdminRights, InputChannel, InputPeerChannel, InputPeerChannelFromMessage, \
    InputPeerChat, InputPeerUser, InputPeerUserFromMessage, InputUser, RestrictionReason, StickerSet
from pyrogram.raw.types.channels import ChannelParticipants
from pyrogram.types import ChatMember, Message
from pyrogram.utils import get_channel_id

from bot.types import EMOJI
from bot.util import get_mention_name, resolve_peer
from main import user_bot

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("req", prefixes="$") & filters.me & ~ filters.forwarded)
async def request(cli: Client, msg: Message) -> None:
    self: types.User = user_bot.me

    log.debug(f"{msg.from_user.id} issued command request")
    log.debug(f" -> text: {msg.text}")

    try:
        peer_id: str = re.search(re.compile(r"(?<=@)?\w{5,}$|^[+-]?\d+$|(?:me|self)$"), msg.command[1])[0]
        log.debug(f"Peer id: {peer_id}")

        if peer_id in ("self", "me"):
            peer_id: str = str(self.id)

    except (IndexError, TypeError):
        await msg.reply_text("Usage: <code>$req &lt;uid|username&gt;</code>")
        return
    else:
        try:
            peer: InputPeer = await resolve_peer(cli, peer_id)
            log.debug(f"Peer instance: {type(peer)}")
        except PeerIdInvalid:
            await msg.reply_text(f"<b><u>ERROR!</u></b>\n"
                                 f"Peer Not Found")
            return
        if isinstance(peer, (InputPeerUser, InputPeerUserFromMessage, InputUser)):
            await msg.reply_text(await parse_user(await cli.send(functions.users.GetFullUser(id=peer))))
        elif isinstance(peer, InputPeerChat):
            # full_chat: ChatFull = await cli.send(functions.messages.GetFullChat(chat_id=-int(telegram_id)))
            await msg.reply_text("Not implemented")
        elif isinstance(peer, (InputPeerChannel, InputPeerChannelFromMessage, InputChannel)):
            await msg.reply_text(
                await parse_channel(cli, await cli.send(functions.channels.GetFullChannel(channel=peer))))
        else:
            await msg.reply_text(f"<b><u>ERROR!</u></b>\n"
                                 f"Peer Not Found")


async def parse_user(uf: UserFull) -> str:
    message: str = f"<b>UID</b>: <code>{uf.user.id}</code>\n" \
                   f"<b>User data center</b>: " \
                   f"<code>{uf.profile_photo.dc_id if uf.profile_photo is not None else None}</code>\n" \
                   f"<b>First Name</b>: " \
                   f"{get_mention_name(uf.user.id, uf.user.first_name)}\n" \
                   f"<b>Last Name</b>: {html.escape(uf.user.last_name if uf.user.last_name else EMOJI.empty)}\n" \
                   f"<b>Username</b>: @{uf.user.username}\n" \
                   f"<b>Bio</b>: \n" \
                   f"<code>{html.escape(uf.about) if uf.about else ''}</code>\n" \
                   f"{EMOJI.true if uf.user.bot else EMOJI.false} <b>Bot</b>\n" \
                   f"{EMOJI.true if uf.user.deleted else EMOJI.false} <b>Deleted</b>\n" \
                   f"{EMOJI.true if uf.user.verified else EMOJI.false} <b>Verified</b>\n" \
                   f"{EMOJI.true if uf.user.scam else EMOJI.false} <b>Scam</b>\n" \
                   f"{EMOJI.true if uf.user.fake else EMOJI.false} <b>Fake</b>\n" \
                   f"{EMOJI.true if uf.user.support else EMOJI.false} <b>Support</b>\n" \
                   f"{EMOJI.true if uf.user.restricted else EMOJI.false} <b>Restricted</b>\n" \
                   f"{EMOJI.true if uf.phone_calls_available else EMOJI.false} <b>Phone call available</b>\n" \
                   f"{EMOJI.true if uf.phone_calls_private else EMOJI.false}" \
                   f" <b>Phone call in privacy setting</b>\n" \
                   f"{EMOJI.true if uf.video_calls_available else EMOJI.false} <b>Video call</b>\n" \
                   f"<b>Groups in common</b>: {uf.common_chats_count}\n"

    restriction_reason: list[RestrictionReason] = uf.user.restriction_reason

    message += parse_res_reason(restriction_reason)

    if uf.user.bot:
        message += parse_bot(uf)
    return message


def parse_bot(uf: UserFull) -> str:
    message: str = f"\n<b><u>Bot</u></b>:\n" \
                   f"{EMOJI.true if uf.user.bot_chat_history else EMOJI.false} read message\n" \
                   f"{EMOJI.false if uf.user.bot_nochats else EMOJI.true} add to group\n" \
                   f"{EMOJI.true if uf.user.bot_inline_geo else EMOJI.false} request geo in inline mode\n" \
                   f"Bot inline placeholder: " \
                   f"<code>{uf.user.bot_inline_placeholder if uf.user.bot_inline_placeholder else ''}</code>\n" \
                   f"Bot info version: <code>{uf.user.bot_info_version}</code>\n" \
                   f"Bot description: \n<code>{uf.bot_info.description if uf.bot_info else None}</code>\n"
    return message


async def parse_channel(cli: Client, chat_full: ChatFull) -> str:
    channel_full: ChannelFull = chat_full.full_chat
    channel: Channel = chat_full.chats[0]
    message: str = f"<b>Chat ID</b>: <code>{get_channel_id(channel_full.id)}</code>\n" \
                   f"<b>Chat Type</b>: <code>{'Channel' if channel.broadcast else 'Supergroup'}</code>\n" \
                   f"<b>Chat Title</b>: <code>{html.escape(channel.title)}</code>\n" \
                   f"<b>Chat Username</b>: @{channel.username}\n" \
                   f"<b>Description</b>:\n" \
                   f"<code>{html.escape(channel_full.about)}</code>\n"

    try:
        admins: list[ChatMember] = await cli.get_chat_members(get_channel_id(channel_full.id), filter="administrators")
    except ChatAdminRequired:
        admins: list = []

    message += f"<b>Administrator counts</b>: <code>{len(admins)}</code>\n" \
               f"<b>Member counts</b>: <code>{channel_full.participants_count}</code>\n" \
               f"{EMOJI.true if channel.verified else EMOJI.false} <b>Verified</b>\n" \
               f"{EMOJI.true if channel.scam else EMOJI.false} <b>Scam</b>\n" \
               f"{EMOJI.true if channel.fake else EMOJI.false} <b>Fake</b>\n" \
               f"{EMOJI.true if channel.signatures else EMOJI.false} <b>Signatures</b>\n" \
               f"{EMOJI.true if channel.restricted else EMOJI.false} <b>Restricted</b>\n"

    restriction_reason: list[RestrictionReason] = channel.restriction_reason

    message += parse_res_reason(restriction_reason)

    if channel_full.pinned_msg_id:
        message += f"🔗 <a href='https://t.me/c/{channel_full.id}/{channel_full.pinned_msg_id}'>Pinned message</a>\n"
    if channel_full.linked_chat_id:
        message += f"🔗 <a href='https://t.me/c/{channel_full.linked_chat_id}/999999999'>Linked Chat</a>\n"

    sticker: StickerSet = channel_full.stickerset
    if sticker:
        message += f"<b>Group Stickers</b>: <a href='https://t.me/addstickers/{sticker.short_name}'>" \
                   f"{html.escape(sticker.title)}</a>\n"
    if not channel.broadcast:
        message += await parse_permission(channel.default_banned_rights)
        message += await parse_channel_admins(cli, channel)

    return message


async def parse_permission(rights: ChatBannedRights) -> str:
    message: str = f"\n<u><b>Chat Permission</b></u>:\n" \
                   f"{EMOJI.false if rights.send_messages else EMOJI.true} <b>send message</b>\n" \
                   f"{EMOJI.false if rights.send_media else EMOJI.true} <b>send media</b>\n" \
                   f"{EMOJI.false if rights.send_stickers else EMOJI.true} <b>send stickers</b>\n" \
                   f"{EMOJI.false if rights.send_gifs else EMOJI.true} <b>send gifs</b>\n" \
                   f"{EMOJI.false if rights.send_games else EMOJI.true} <b>send games</b>\n" \
                   f"{EMOJI.false if rights.send_inline else EMOJI.true} <b>send inline</b>\n" \
                   f"{EMOJI.false if rights.embed_links else EMOJI.true} <b>embed links</b>\n" \
                   f"{EMOJI.false if rights.send_polls else EMOJI.true} <b>send polls</b>\n" \
                   f"{EMOJI.false if rights.change_info else EMOJI.true} <b>change info</b>\n" \
                   f"{EMOJI.false if rights.invite_users else EMOJI.true} <b>invite users</b>\n" \
                   f"{EMOJI.false if rights.pin_messages else EMOJI.true} <b>pin messages</b>\n"
    return message


async def parse_channel_admins(cli: Client, channel: Channel) -> str:
    peer = await cli.resolve_peer(utils.get_channel_id(channel.id))

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
                   f"{get_mention_name(user_creator.id, user_creator.first_name, user_creator.last_name)}\n"

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
               f"{get_mention_name(_.user_id, users[_.user_id].first_name, users[_.user_id].last_name)}\n"

    return ret


def parse_res_reason(restriction_reason) -> str:
    message: str = ""

    if restriction_reason:
        message = f"\n<b>Restriction reason(s)</b>:\n"
        for reason in restriction_reason:
            message += f"-> <code>{reason.platform} - {reason.reason}</code>\n" \
                       f"   {reason.text}\n"

    return message
