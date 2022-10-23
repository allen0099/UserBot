from pyrogram import types
from pyrogram.enums import ChatMemberStatus
from pyrogram.filters import Filter, create
from pyrogram.types import Message

from bot import Bot

PERMISSION_DENIED: str = "<b>Permission denied</b>"


async def __filter_function(flt: Filter, cli: Bot, msg: Message) -> bool:
    admins: list[types.ChatMember] = await cli.get_chat_admins(msg.chat.id)

    if msg.sender_chat:

        if msg.sender_chat.id == msg.chat.id:
            return True

        return False

    me: types.ChatMember = await cli.get_chat_member(msg.chat.id, cli.me.id)

    if me.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return False

    privileges: types.ChatPrivileges = me.privileges

    if not privileges.can_restrict_members or not privileges.can_delete_messages:
        await msg.reply_text(PERMISSION_DENIED)
        return False

    if msg.from_user.id not in [_.user.id for _ in admins]:
        await msg.reply_text(PERMISSION_DENIED)
        return False

    return True


admin_required: Filter = create(__filter_function)
