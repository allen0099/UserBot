import logging
import re
from typing import Union

from pyrogram import Client, raw, utils
from pyrogram.errors import PeerIdInvalid

log: logging = logging.getLogger(__name__)


async def resolve_peer(
        cli: Client,
        peer_id: Union[int, str]
) -> raw.base.InputPeer:
    """Removed phone number check. Other are same as ``client.resolve_peer``.

    .. note::

        This is a utility method intended to be used **only** when working with raw
        :obj:`functions <pyrogram.api.functions>` (i.e: a Telegram API method you wish to use which is not
        available yet in the Client class as an easy-to-use method).

    Parameters:
        cli (``<pyrogram.Client>``):
            The client you use to connect to Telegram.
        peer_id (``int`` | ``str``):
            The peer id you want to extract the InputPeer from.
            Can be a direct id (int), a username (str).

    Returns:
        ``InputPeer``: On success, the resolved peer id is returned in form of an InputPeer object.

    Raises:
        KeyError: In case the peer doesn't exist in the internal database.
    """
    try:
        return await cli.storage.get_peer_by_id(peer_id)
    except KeyError:
        # key not found
        peer_id = re.sub(r"[@+\s]", "", peer_id.lower())
        try:
            peer_id = int(peer_id)
        except ValueError:
            return await _string_exe(cli, peer_id)
        else:
            peer_type = utils.get_peer_type(peer_id)

            if peer_type == "user":
                await cli.fetch_peers(
                    await cli.send(
                        raw.functions.users.GetUsers(
                            id=[
                                raw.types.InputUser(
                                    user_id=peer_id,
                                    access_hash=0
                                )
                            ]
                        )
                    )
                )
            elif peer_type == "chat":
                await cli.send(
                    raw.functions.messages.GetChats(
                        id=[-peer_id]
                    )
                )
            else:
                await cli.send(
                    raw.functions.channels.GetChannels(
                        id=[
                            raw.types.InputChannel(
                                channel_id=utils.get_channel_id(peer_id),
                                access_hash=0
                            )
                        ]
                    )
                )

            try:
                return await cli.storage.get_peer_by_id(peer_id)
            except KeyError:
                raise PeerIdInvalid


async def _string_exe(cli, peer_id):
    if peer_id in ("self", "me"):
        return raw.types.InputPeerSelf()
    try:
        return await cli.storage.get_peer_by_username(peer_id)
    except KeyError:
        await cli.send(
            raw.functions.contacts.ResolveUsername(
                username=peer_id
            )
        )

        return await cli.storage.get_peer_by_username(peer_id)
