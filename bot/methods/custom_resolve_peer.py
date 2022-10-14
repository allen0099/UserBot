import re
import warnings

from pyrogram import raw, utils
from pyrogram.errors import PeerIdInvalid

import bot


class CustomResolvePeer:
    async def custom_resolve_peer(
        self: "bot.Bot", peer_id: int | str
    ) -> raw.base.InputPeer:
        """
        Removed phone number check. Other are same as ``client.resolve_peer``.
        Modified pyrogram version: 2.0.57

        Args:
            peer_id:

        Returns:

        """
        warnings.warn("This function is not fully tested!")

        if not self.is_connected:
            raise ConnectionError("Client has not been started yet")

        try:
            return await self.storage.get_peer_by_id(peer_id)
        except KeyError:
            # key not found
            return await _check(self, peer_id)


async def _check(
    cli: "bot.Bot",
    peer_id: int | str,
) -> raw.base.InputPeer | raw.base.InputUser | raw.base.InputChannel:
    if isinstance(peer_id, str):
        if peer_id in ("self", "me"):
            return raw.types.InputPeerSelf()

        peer_id = re.sub(r"[@+\s]", "", peer_id.lower())

        try:
            int(peer_id)
        except ValueError:
            try:
                return await cli.storage.get_peer_by_username(peer_id)
            except KeyError:
                await cli.invoke(
                    raw.functions.contacts.ResolveUsername(username=peer_id)
                )

                return await cli.storage.get_peer_by_username(peer_id)
        else:
            raise PeerIdInvalid

    peer_type = utils.get_peer_type(peer_id)

    if peer_type == "user":
        await cli.fetch_peers(
            await cli.invoke(
                raw.functions.users.GetUsers(
                    id=[raw.types.InputUser(user_id=peer_id, access_hash=0)]
                )
            )
        )
    elif peer_type == "chat":
        await cli.invoke(raw.functions.messages.GetChats(id=[-peer_id]))
    else:
        await cli.invoke(
            raw.functions.channels.GetChannels(
                id=[
                    raw.types.InputChannel(
                        channel_id=utils.get_channel_id(peer_id), access_hash=0
                    )
                ]
            )
        )

    try:
        return await cli.storage.get_peer_by_id(peer_id)
    except KeyError:
        raise PeerIdInvalid
