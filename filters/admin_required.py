import logging

from pyrogram import Client
from pyrogram.filters import Filter, create
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import ChatMember, Message

from bot.functions import CustomFunctions
from main import user_bot

log: logging.Logger = logging.getLogger(__name__)


async def __filter_function(flt: Filter, cli: Client, msg: Message):
    admins: list[ChatMember] = await CustomFunctions.get_members(cli, msg.chat.id, choose=Filters.ADMINISTRATORS)
    if msg.from_user.id not in [_.user.id for _ in admins]:
        await msg.reply_text("<b>Permission denied</b>")
        return False

    me: ChatMember = await cli.get_chat_member(msg.chat.id, user_bot.me.id)
    if not me.can_restrict_members or not me.can_delete_messages:
        await msg.reply_text("<b>Permission denied</b>")
        return False

    return True


_admin_required: Filter = create(__filter_function)
