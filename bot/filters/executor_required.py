from pyrogram import types
from pyrogram.filters import Filter, create
from pyrogram.types import Message

from bot import Bot
from database.models.users import Users


async def __filter_function(flt: Filter, cli: Bot, msg: Message) -> bool:
    if msg.sender_chat:
        return False

    executors: list[Users] = Users.get_executors()
    me: types.User = cli.me

    if msg.from_user.id not in [_.id for _ in executors] + [me.id]:
        return False

    return True


executor_required: Filter = create(__filter_function)
