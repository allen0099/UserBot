import logging

from pyrogram import Client, filters, types
from pyrogram.enums import ChatType

from bot import Bot
from bot.validation import UserValidator
from core.decorator import event_log
from core.log import event_logger, main_logger
from database.models.privilege import Privilege
from database.models.users import Users

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(filters.group & ~filters.media_group, group=-98)
@event_log()
async def message_handler(cli: Bot, msg: types.Message) -> None:
    if msg.chat.type != ChatType.SUPERGROUP:
        return

    if msg.chat.id in Privilege.admin_group_list() and msg.from_user is not None:
        uv: UserValidator = UserValidator(msg.from_user)
        uv.validate()

        if uv.errors:
            await cli.set_user_black(
                msg.from_user, msg, uv.errors, uv.error_messages, ["message"]
            )

        else:
            u: Users = Users.get(msg.from_user.id)
            u.add()
