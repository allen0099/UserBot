import asyncio

from pyrogram import raw
from pyrogram.errors import FloodWait

import bot


class GetFullChannel:
    async def get_full_channel(
        self: "bot.Bot",
        chat_id: int | str,
    ) -> raw.types.ChannelFull:
        peer: raw.base.InputPeer = await self.custom_resolve_peer(chat_id)

        if isinstance(
            peer,
            (
                raw.types.InputPeerChannel,
                raw.types.InputPeerChannelFromMessage,
                raw.types.InputChannel,
            ),
        ):
            try:
                r: raw.types.messages.ChatFull = await self.invoke(
                    raw.functions.channels.GetFullChannel(channel=peer)
                )

                return r.full_chat

            except FloodWait as error:
                await asyncio.sleep(error.value)

                await self.get_full_channel(chat_id)

        raise TypeError(f"Not a channel, chat_id: {chat_id}, peertype: {type(peer)}")
