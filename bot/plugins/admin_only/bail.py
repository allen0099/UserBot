import logging

from pyrogram import Client, filters, types
from pyrogram.enums import ChatMembersFilter

from bot import Bot
from bot.filters import admin_required
from bot.functions import msg_auto_clean
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger

log: logging.Logger = event_logger(__name__)

__USAGE__: str = "Usage: <code>bail {kick|restrict}</code>"
KICKED: list[str] = ["kick", "kicked"]
RESTRICTED: list[str] = ["restrict", "restricted"]


@Client.on_message(
    filters.command("bail", prefixes=COMMAND_PREFIXES)
    & admin_required
    & filters.group
    & ~filters.forwarded
)
@event_log()
async def bail(cli: Bot, msg: types.Message) -> None:
    await msg.delete()

    if len(msg.command) == 2:
        log.debug(f"Bailing out {msg.command[1].lower()} users in {msg.chat.id}...")

        if msg.command[1].lower() in KICKED:
            members: list[types.ChatMember] = [
                user
                async for user in cli.get_chat_members(
                    msg.chat.id, filter=ChatMembersFilter.BANNED
                )
            ]

        elif msg.command[1].lower() in RESTRICTED:
            members: list[types.ChatMember] = [
                user
                async for user in cli.get_chat_members(
                    msg.chat.id, filter=ChatMembersFilter.RESTRICTED
                )
            ]

        else:
            await msg.reply_text(__USAGE__)
            return

    else:
        await msg.reply_text(__USAGE__)
        return

    count: int = 0
    log.debug(f"{len(members)} found!")

    message: types.Message = await cli.send_message(
        msg.chat.id, f"Cleaning the list...({count}/{len(members)})"
    )

    for member in members:
        count += 1

        log.debug(f"Bailing out uid: {member.user.id}")
        log.debug(f"Progress: {count}/{len(members)}")

        if count % 50 == 1:
            await message.edit(f"Cleaning the list...({count}/{len(members)})")

        await cli.unban_chat_member(msg.chat.id, member.user.id)

    log.debug("Bail finished!")
    await msg_auto_clean(
        await message.edit(f"{count} <b><u>{msg.command[1]} user(s)</u></b> released!")
    )
