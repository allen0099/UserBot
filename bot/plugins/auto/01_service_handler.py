import logging

from pyrogram import Client, enums, filters, types

from bot import Bot
from bot.enums import LogTopics
from bot.functions import get_chat_link
from bot.validation import UserValidator
from core.decorator import event_log
from core.log import event_logger, main_logger
from database.models.privilege import Privilege
from database.models.users import Users

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(filters.group & ~filters.media_group, group=-100)
@event_log()
async def service_handler(cli: Bot, msg: types.Message) -> None:
    """
    Ban user if user is in blacklist when user try to join the group.
    """
    if not msg.service:
        return

    if msg.chat.type != enums.ChatType.SUPERGROUP:
        return

    match msg.service:
        case enums.MessageServiceType.NEW_CHAT_MEMBERS:
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
                        await cli.set_user_black(
                            user, msg, uv.errors, uv.error_messages, ["join"]
                        )
                        continue

                    await cli.send_log_message(
                        f"User: {user.mention}\n"
                        f"User ID: <code>{user.id}</code>\n"
                        f"Joined: {get_chat_link(msg.chat)}\n"
                        f"Message Link: {msg.link}",
                        LogTopics.new_user,
                    )
                    u.add()

        case enums.MessageServiceType.LEFT_CHAT_MEMBERS if msg.left_chat_member.is_self:
            logger.info(
                f"Admin {repr(msg.from_user)} kicked me from {repr(msg.chat)}. Hope to see them again!"
            )

        case _:
            logger.debug(f"{msg.service} is not handled, skipping...")

    msg.stop_propagation()


@Client.on_chat_member_updated(filters.group, group=-101)
def new_member(cli: Bot, chat_member_updated: types.ChatMemberUpdated):
    message: str = ""
    if chat_member_updated.from_user:
        message += (
            f"User: {chat_member_updated.from_user.mention}\n"
            f"User ID: <code>{chat_member_updated.from_user.id}</code>\n"
        )

    if chat_member_updated.old_chat_member:
        message += (
            f"Old User: {chat_member_updated.old_chat_member.user.mention}\n"
            f"Old ID: <code>{chat_member_updated.old_chat_member.user.id}</code>\n"
        )

    if chat_member_updated.new_chat_member:
        message += (
            f"New User: {chat_member_updated.new_chat_member.user.mention}\n"
            f"New ID: <code>{chat_member_updated.new_chat_member.user.id}</code>\n"
        )

    if chat_member_updated.chat:
        message += (
            f"Chat: {get_chat_link(chat_member_updated.chat)}\n"
            f"Chat ID: <code>{chat_member_updated.chat.id}</code>\n"
        )

    if chat_member_updated.invite_link:
        message += f"Invite Link: {chat_member_updated.invite_link}\n"

    await cli.send_log_message(
        message,
        LogTopics.debug,
    )
