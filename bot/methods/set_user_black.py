import logging

from pyrogram import types

import bot
from bot.enums import LogTopics, PermissionLevel
from bot.functions import get_chat_link
from core import main_logger

log: logging.Logger = main_logger(__name__)


class SetUserBlack:
    async def set_user_black(
        self: "bot.Bot",
        user: types.User,
        msg: types.Message,
        errors: list[str],
        error_messages: dict[str, ...] = None,
        additional_tags: list[str] = None,
    ) -> None:
        from database.models.action_logs import ActionLogs
        from database.models.users import Users

        u: Users = Users.get(msg.from_user.id)

        if additional_tags:
            header: str = f"#banned #{' #'.join(additional_tags)}#{' #'.join(errors)}\n"

        else:
            header: str = f"#banned #{' #'.join(errors)}\n"

        if error_messages:
            footer: str = f"錯誤訊息：\n"
            for error, value in error_messages.items():
                footer += f"{error}：{value}\n"

        else:
            footer: str = ""

        await self.send_log_message(
            f"{header}"
            f"使用者：{user.mention} <code>{user.id}</code>\n"
            f"群組：{get_chat_link(msg.chat)} <code>{msg.chat.id}</code>\n"
            f"連結：{msg.link}\n"
            f"{footer}",
            LogTopics.banned,
        )

        u.update(PermissionLevel.BLACK)

        await self.ban_chat_member(msg.chat.id, user.id)
        await self.delete_user_history(msg.chat.id, user.id)

        ActionLogs.create(user.id, msg.chat.id, f"原因：{errors}", "", repr(msg))
