import logging

from pyrogram import errors, raw
from pyrogram.raw import types

import bot
from core import main_logger

log: logging.Logger = main_logger(__name__)


class SetAntiSpam:
    async def _set_anti_spam(
        self: "bot.Bot",
        chat_id: int | str,
        enabled: bool,
    ) -> None:
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

                return

            except errors.exceptions.bad_request_400.ChatNotModified as e:
                log.critical(f"{e.MESSAGE}, chat={chat_id}, enabled={enabled}")
                return

        raise TypeError("Invalid chat type")
