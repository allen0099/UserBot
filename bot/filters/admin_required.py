import warnings

from pyrogram import types
from pyrogram.filters import Filter, create
from pyrogram.types import Message

from bot import Bot


async def __filter_function(flt: Filter, cli: Bot, msg: Message) -> bool:
    warnings.warn("This filter is not tested yet.")

    admins: list[types.ChatMember] = await cli.get_chat_admins(msg.chat.id)

    if msg.from_user.id not in [_.user.id for _ in admins]:
        await msg.reply_text("<b>Permission denied</b>")
        return False

    me: types.ChatMember = await cli.get_chat_member(msg.chat.id, cli.me.id)

    privileges: types.ChatPrivileges = me.privileges

    if not privileges.can_restrict_members or not privileges.can_delete_messages:
        await msg.reply_text("<b>Permission denied</b>")
        return False

    return True


admin_required: Filter = create(__filter_function)
