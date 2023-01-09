import logging

from pyrogram import Client
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.enums import MessageServiceType
from pyrogram.types import Message

from bot import Bot
from bot.enums import PermissionLevel
from bot.functions import get_chat_link
from bot.methods.send_log_message import LogTopics
from bot.validation import UserValidator
from core.decorator import event_log
from core.log import event_logger, main_logger
from database.models.privilege import Privilege
from database.models.users import Users

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(filters.group & ~filters.media_group, group=-100)
@event_log()
async def service_handler(cli: Bot, msg: Message) -> None:
    """
    Ban user if user is in blacklist when user try to join the group.
    """
    if not msg.service:
        return

    if msg.chat.type != ChatType.SUPERGROUP:
        return

    match msg.service:
        case MessageServiceType.NEW_CHAT_MEMBERS:
            if cli.me in msg.new_chat_members:
                await cli.send_log_message(
                    f"#join\n"
                    f"I joined {get_chat_link(msg.chat)} at {msg.date.isoformat()}",
                    LogTopics.auto,
                )
                return

            if msg.chat.id in Privilege.admin_group_list():
                # Admin permission, checking blacklist users

                for user in msg.new_chat_members:
                    uv: UserValidator = UserValidator(user)
                    uv.validate()
                    u: Users = Users.get(msg.from_user.id)

                    if uv.errors:
                        await cli.send_log_message(
                            f"#banned "
                            f"#{' #'.join(uv.errors)}\n"
                            f"User: {user.mention}\n"
                            f"User ID: <code>{user.id}</code>\n"
                            f"Joined: {get_chat_link(msg.chat)}\n"
                            f"Message Link: {msg.link}",
                            LogTopics.banned,
                        )
                        u.update(PermissionLevel.BLACK)
                        # TODO: act something ban user (implement in next version)

                        await cli.ban_chat_member(msg.chat.id, user.id)
                        await cli.delete_user_history(msg.chat.id, user.id)

                        continue

                    await cli.send_log_message(
                        f"User: {user.mention}\n"
                        f"User ID: <code>{user.id}</code>\n"
                        f"Joined: {get_chat_link(msg.chat)}\n"
                        f"Message Link: {msg.link}",
                        LogTopics.new_user,
                    )
                    u.add()

        case MessageServiceType.LEFT_CHAT_MEMBERS if msg.left_chat_member.is_self:
            logger.info(
                f"Admin {repr(msg.from_user)} kicked me from {repr(msg.chat)}. Hope to see them again!"
            )

        case _:
            logger.debug(f"{msg.service} is not handled, skipping...")

    msg.stop_propagation()
