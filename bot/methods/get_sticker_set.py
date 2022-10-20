from pyrogram import raw

import bot


class GetStickerSet:
    async def get_sticker_set(
        self: "bot.Bot",
        short_name: str,
    ) -> raw.base.messages.StickerSet:
        r: raw.base.messages.StickerSet = await self.invoke(
            raw.functions.messages.GetStickerSet(
                hash=0,
                stickerset=raw.types.InputStickerSetShortName(
                    short_name=short_name,
                ),
            )
        )

        return r.set
