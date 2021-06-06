import logging

from pyrogram import Client
from pyrogram.filters import Filter, create
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import ChatMember, Message

from bot.functions import get_members
from main import user_bot

log: logging.Logger = logging.getLogger(__name__)


async def admin_required_filter(flt: Filter, cli: Client, msg: Message):
    admins: list[ChatMember] = await get_members(cli, msg.chat.id, choose=Filters.ADMINISTRATORS)
    if msg.from_user.id not in [_.user.id for _ in admins]:
        await msg.reply_text("<b>Permission denied</b>")
        return False

    me: ChatMember = await cli.get_chat_member(msg.chat.id, user_bot.me.id)
    if not me.can_restrict_members or not me.can_delete_messages:
        await msg.reply_text("<b>Permission denied</b>")
        return False

    return True


admin_required = create(admin_required_filter)
