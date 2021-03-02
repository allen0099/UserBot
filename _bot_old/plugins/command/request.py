import html
import logging
import re
from typing import List, Union, Tuple

import pyrogram
from pyrogram import Client, Filters, Message
from pyrogram.api import types, functions
from pyrogram.errors import PeerIdInvalid, UsernameInvalid

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("req", prefixes="$") & Filters.me)
def request(cli: Client, msg: Message) -> None:
    if len(msg.command) == 1 or len(msg.command) >= 3:
        msg.reply_text("Usage: <code>$req [NAME]</code>\n"
                       "\n"
                       "Request the group or a user's information\n"
                       " - NAME: int for UID, str for @username\n")
    elif len(msg.command) == 2:
        username_re = re.compile(r"(?<=t\.me/)\w{5,}$|(?<=@)\w{5,}$|\w{5,}$|^[+-]?\d+$|me$|self$")
        cmd: str = re.search(username_re, msg.command[1])[0]
        photo: Union[str, None] = None
        file_ref: Union[str, None] = None
        try:
            peer: Union[
                types.InputPeerChannel,
                types.InputPeerChat,
                types.InputPeerSelf,
                types.InputPeerUser] = cli.resolve_peer(cmd)
            photo, file_ref = _parse_photo(cli, cmd)
        except PeerIdInvalid as e:
            string: str = str(e.CODE) + " " + e.ID
        except UsernameInvalid as e:
            string: str = str(e.CODE) + " " + e.ID
        else:
            string: str
            string = _parse(cli, peer)
        if photo is not None:
            if len(string) < 1024:
                msg.reply_photo(photo, file_ref=file_ref, caption=string)
            else:
                msg.reply_photo(photo, file_ref=file_ref)
                msg.reply_text(string, parse_mode="HTML")
        else:
            msg.reply_text(string, parse_mode="HTML")


def _parse(cli: Client,
           peer: Union[
               types.InputPeerChannel,
               types.InputPeerChat,
               types.InputPeerSelf,
               types.InputPeerUser]) -> str:
    if isinstance(peer, (types.InputPeerUser, types.InputPeerSelf)):
        """User, bot or self"""
        api_user: types.UserFull = cli.send(
            functions.users.GetFullUser(
                id=peer
            )
        )
        user: types.User = api_user.user

        return _parse_user(api_user, user)
    elif isinstance(peer, types.InputPeerChannel):
        """Super group or channel"""
        api_channel: types.messages.ChatFull = cli.send(
            functions.channels.GetFullChannel(
                channel=peer
            )
        )
        channel: types.Channel = api_channel.chats[0]
        channel_full: types.ChannelFull = api_channel.full_chat

        return _parse_channel(cli, channel, channel_full)
    elif isinstance(peer, types.InputPeerChat):
        """Normal chat"""
        api_chat: types.messages.ChatFull = cli.send(
            functions.messages.GetFullChat(
                chat_id=peer.chat_id
            )
        )
        chat: types.Chat = api_chat.chats[0]
        chat_full: types.ChatFull = api_chat.full_chat
        users: List[types.User] = api_chat.users
        return _parse_chat(chat, chat_full, users)
    else:
        log.warning(f"Peer undefined, peer type is {peer.QUALNAME}")


def _parse_photo(cli: Client, cmd: str) -> Union[Tuple[None, None], Tuple[str, str]]:
    photos: List[pyrogram.Photo] = cli.get_profile_photos(cmd)
    if not photos:
        return None, None
    else:
        latest_photo = photos[0]
        return latest_photo.file_id, latest_photo.file_ref


def _parse_user(api_user: types.UserFull, user: types.User) -> str:
    _s: str = f"UID: <code>{user.id}</code>\n" \
              f"User data center: <code>{getattr(user.photo, 'dc_id', None)}</code>\n" \
              f"First Name: <a href='tg://user?id={user.id}'>{html.escape(str(user.first_name))}</a>\n" \
              f"Last Name: {html.escape(str(user.last_name))}\n" \
              f"Username: @{user.username}\n" \
              f"Bio: \n" \
              f"<code>{html.escape(str(api_user.about))}</code>\n" \
              f"Bot: {'✅' if user.bot else '❎'}\n" \
              f"Deleted: {'✅' if user.deleted else '❎'}\n" \
              f"Verified: {'✅' if user.verified else '❎'}\n" \
              f"Scam: {'✅' if user.scam else '❎'}\n" \
              f"Support: {'✅' if user.support else '❎'}\n" \
              f"Phone calls available: {'✅' if api_user.phone_calls_available else '❎'}\n" \
              f"Phone calls private: {'✅' if api_user.phone_calls_private else '❎'}\n" \
              f"Groups in common: {api_user.common_chats_count}\n"
    return _s


def _parse_channel(cli: Client, channel: types.Channel, channel_full: types.ChannelFull) -> str:
    # noinspection PyTypeChecker
    _s: str = f"Chat ID: <code>{-1000000000000 - channel.id}</code>\n" \
              f"Chat type: <code>{'Supergroup' if channel.megagroup else 'Channel'}</code>\n" \
              f"Chat title: {html.escape(channel.title)}\n" \
              f"Chat username: @{getattr(channel, 'username', None)}\n" \
              f"Description:\n" \
              f"<code>{html.escape(channel_full.about)}</code>\n" \
              f"Administrators: {len(cli.get_chat_members(-1000000000000 - channel.id, filter='administrators')) if channel.megagroup else None}\n" \
              f"Members: {channel_full.participants_count}\n" \
              f"Verified: {'✅' if channel.verified else '❎'}\n" \
              f"Scam: {'✅' if channel.scam else '❎'}\n" \
              f"Restricted: {'✅' if channel.restricted else '❎'}\n"
    if channel.restricted:
        _s += f"Restriction reason:\n"
        for reason in channel.restriction_reason:
            restriction_reason: types.RestrictionReason = reason
            _s += f"  <code>{restriction_reason.platform} - {restriction_reason.reason}</code>\n" \
                  f"  {restriction_reason.text}\n"
    if channel_full.pinned_msg_id is not None:
        _s += f"<a href='https://t.me/c/{channel.id}/{channel_full.pinned_msg_id}'>Pinned message</a>\n"
    if channel_full.stickerset is not None:
        _s += f"Group Stickers: " \
              f"<a href='https://t.me/addstickers/{channel_full.stickerset.short_name}'>" \
              f"{html.escape(channel_full.stickerset.title)}</a>\n"

    if channel.megagroup:
        # List all default permissions
        permission: types.ChatBannedRights = channel.default_banned_rights

        _s += string_permission(permission)

        # noinspection PyTypeChecker
        # Listing all admins
        admins: List[pyrogram.ChatMember] = cli.get_chat_members(-1000000000000 - channel.id,
                                                                 filter="administrators")
        admins.sort(key=lambda x: x.user.id)

        _s += string_admins(admins)
    return _s


def _parse_chat(chat: types.Chat, chat_full: types.ChatFull, users: List[types.User]) -> str:
    _s: str = f"Chat ID: <code>-{chat.id}</code>\n" \
              f"Chat type: <code>Chat(Normal Group)</code>\n" \
              f"Chat title: {html.escape(chat.title)}\n" \
              f"Description:\n" \
              f"<code>{html.escape(chat_full.about)}</code>\n" \
              f"Members: {chat.participants_count}\n"
    if chat_full.pinned_msg_id is not None:
        _s += f"<a href='https://t.me/c/{chat.id}/{chat_full.pinned_msg_id}'>Pinned message</a>\n"

    permission: types.ChatBannedRights = chat.default_banned_rights
    _s += string_permission(permission)

    return _s


def string_permission(permission: types.ChatBannedRights) -> str:
    permission_string = f"\nDefault permissions:\n" \
                        f"{'✅' if not permission.send_messages else '❎'} send messages\n" \
                        f"{'✅' if not permission.send_media else '❎'} send media\n" \
                        f"{'✅' if not permission.send_stickers else '❎'} send stickers\n" \
                        f"{'✅' if not permission.send_gifs else '❎'} send GIFs\n" \
                        f"{'✅' if not permission.embed_links else '❎'} embed links\n" \
                        f"{'✅' if not permission.send_polls else '❎'} send polls\n" \
                        f"{'✅' if not permission.send_games else '❎'} send games\n" \
                        f"{'✅' if not permission.send_inline else '❎'} send inline\n" \
                        f"{'✅' if not permission.invite_users else '❎'} invite users\n" \
                        f"{'✅' if not permission.pin_messages else '❎'} pin message\n" \
                        f"{'✅' if not permission.change_info else '❎'} change group info\n"
    return permission_string


def string_admins(admins: List[pyrogram.ChatMember]) -> str:
    creator: pyrogram.ChatMember = [c for c in admins if c.status == "creator"][0]
    bots: List[pyrogram.ChatMember] = [c for c in admins if c.user.is_bot]

    admins_string = f"\nAdministrators:\n" \
                    f"Creator: " \
                    f"<code>[{creator.title if creator.title is not None else ''}]</code>" \
                    f"<a href='tg://user?id={creator.user.id}'>" \
                    f"{creator.user.first_name} " \
                    f"{creator.user.last_name if creator.user.last_name is not None else ''}</a>\n"

    # remove redundant
    admins.remove(creator)
    for bot in bots:
        admins.remove(bot)

    # append admins
    for admin in admins:
        admins_string += f"<code>[{admin.title if admin.title is not None else ''}]</code>" \
                         f"<a href='tg://user?id={admin.user.id}'>" \
                         f"{admin.user.first_name} " \
                         f"{admin.user.last_name if admin.user.last_name is not None else ''}</a>\n"
    for bot in bots:
        admins_string += f"<code>[{bot.title if bot.title is not None else ''}]</code>" \
                         f"<a href='tg://user?id={bot.user.id}'>" \
                         f"{bot.user.first_name} " \
                         f"{bot.user.last_name if bot.user.last_name is not None else ''}</a> (🤖)\n"
    return admins_string
