from pyrogram import raw

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
            r: raw.types.messages.ChatFull = await self.invoke(
                raw.functions.channels.GetFullChannel(channel=peer)
            )

            return r.full_chat

        raise TypeError("Not a channel")
