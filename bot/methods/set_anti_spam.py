import logging

from pyrogram import raw
from pyrogram.errors import ChatAdminRequired, ChatNotModified
from pyrogram.raw import types

import bot
from core import main_logger

log: logging.Logger = main_logger(__name__)


class SetAntiSpam:
    async def _set_anti_spam(
        self: "bot.Bot",
        chat_id: int | str,
        enabled: bool,
    ) -> bool:
        channel = await self.custom_resolve_peer(chat_id)

        if isinstance(
            channel,
            (
                raw.types.InputPeerChannel,
                raw.types.InputPeerChannelFromMessage,
                raw.types.InputChannel,
            ),
        ):
            try:
                _: types.Updates = await self.invoke(
                    raw.functions.channels.ToggleAntiSpam(
                        channel=channel,
                        enabled=enabled,
                    )
                )

                return True

            except (ChatNotModified, ChatAdminRequired) as e:
                log.critical(f"{e.MESSAGE}, chat={chat_id}, enabled={enabled}")
                return False

        raise TypeError("Invalid chat type")
