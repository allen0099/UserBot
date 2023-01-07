import logging
import time

from pyrogram import Client, filters, types
from pyrogram.types import Message

from bot import Bot
from bot.enums import PermissionLevel
from bot.filters import executor_required
from bot.functions import get_chat_link, get_target, is_protected, msg_auto_clean
from bot.methods.send_log_message import LogTopics
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger
from database.models.action_logs import ActionLogs
from database.models.privilege import Privilege
from database.models.users import Users

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("gban", prefixes=COMMAND_PREFIXES)
    & executor_required
    & filters.group
    & ~filters.forwarded
)
@event_log()
async def global_ban(cli: Bot, msg: Message) -> None:
    # noinspection DuplicatedCode
    await msg.delete()

    start_time: float = time.perf_counter()
    target: types.User | types.Chat = await get_target(cli, msg)
    exec_info: str = (
        f"執行者：{msg.from_user.mention} (<code>{msg.from_user.id}</code>)\n"
        f"執行位置：{get_chat_link(msg.chat)} (<code>{msg.chat.id}</code>)\n"
        f"執行：<b><u>全域封鎖</u></b>"
    )

    if isinstance(target, types.User):
        target_info: str = f"{target.mention} (<code>{target.id}</code>)"

    else:
        target_info: str = f"{get_chat_link(target)} (<code>{target.id}</code>)"

    if is_protected(target):
        await cli.send_log_message(
            f"❌ #gban\n{exec_info}\n目標：{target_info}\n原因：目標受到保護，操作失敗。",
            LogTopics.auto,
        )
        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                f"操作失敗",
            )
        )
        return

    u: Users = Users.get(target.id)
    u.update(PermissionLevel.BLACK)

    if isinstance(target, types.User):
        counter: int = 0
        common_chats: list[types.Chat] = await target.get_common_chats()
        groups: list[int] = Privilege.admin_group_list()
        ban_message: str = f"已將 {target_info} 從下列群組中封鎖：\n"

        for chat in common_chats:
            if chat.id in groups:
                counter += 1

                ban_message += f"{get_chat_link(chat)} (<code>{chat.id}</code>)\n"
                ActionLogs.create_user_gban_log(target.id, chat.id, msg.from_user.id)

                await cli.ban_chat_member(chat.id, target.id)
                await cli.delete_user_history(chat.id, target.id)

        time_: float = time.perf_counter() - start_time
        short_info: str = (
            f"共封鎖了 <code>{counter}</code> 個群組，耗時 <code>{time_:.2f}</code> 秒。"
        )

        await cli.send_log_message(
            f"✅ #gban\n{exec_info}\n{ban_message}\n{short_info}",
            LogTopics.auto,
        )

        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                short_info,
                disable_web_page_preview=True,
            )
        )

    else:
        ActionLogs.create_chat_gban_log(target.id, msg.from_user.id)
        time_: float = time.perf_counter() - start_time
        short_info: str = f"封鎖了 {target_info} 耗時 <code>{time_:.2f}</code> 秒。"

        await cli.send_log_message(
            f"✅ #gban #chat\n{exec_info}\n{short_info}",
            LogTopics.auto,
        )

        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                short_info,
                disable_web_page_preview=True,
            )
        )


@Client.on_message(
    filters.command("ungban", prefixes=COMMAND_PREFIXES)
    & executor_required
    & filters.group
    & ~filters.forwarded
)
async def undo_global_ban(cli: Bot, msg: Message) -> None:
    # noinspection DuplicatedCode
    await msg.delete()

    start_time: float = time.perf_counter()
    target: types.User | types.Chat = await get_target(cli, msg)
    exec_info: str = (
        f"執行者：{msg.from_user.mention} (<code>{msg.from_user.id}</code>)\n"
        f"執行位置：{get_chat_link(msg.chat)} (<code>{msg.chat.id}</code>)\n"
        f"執行：<b><u>全域解除封鎖</u></b>"
    )

    if isinstance(target, types.User):
        target_info: str = f"{target.mention} (<code>{target.id}</code>)"

    else:
        target_info: str = f"{get_chat_link(target)} (<code>{target.id}</code>)"

    u: Users = Users.get(target.id)

    if u.mock:
        await cli.send_log_message(
            f"❌ #gban #unblock\n{exec_info}\n目標：{target_info}\n原因：使用者不在資料庫中，操作失敗。",
            LogTopics.auto,
        )
        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                f"操作失敗",
            )
        )
        return

    u.update()

    if isinstance(target, types.User):
        unban_message: str = f"已將 {target_info} 從下列群組中解除封鎖：\n"
        action_logs: list["ActionLogs"] = ActionLogs.get_gban_logs(target.id)
        counter: int = 0

        for _log in action_logs:
            try:
                await cli.unban_chat_member(_log.group_id, target.id)
                c: types.Chat = await cli.get_chat(_log.group_id)
                unban_message += f"{get_chat_link(c)} (<code>{c.id}</code>)\n"
                counter += 1

            except Exception as e:
                await cli.send_log_message(
                    "❌ #gban #unblock\n" + str(e), LogTopics.error
                )

        time_: float = time.perf_counter() - start_time
        short_info: str = (
            f"共解除了 <code>{counter}</code> 個群組，耗時 <code>{time_:.2f}</code> 秒。"
        )

        await cli.send_log_message(
            f"✅ #gban #unblock\n{exec_info}\n{unban_message}\n{short_info}",
            LogTopics.auto,
        )

        ActionLogs.destroy(target.id)

        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                short_info,
                disable_web_page_preview=True,
            )
        )

    else:
        time_: float = time.perf_counter() - start_time
        short_info: str = f"已將 {target_info} 解除封鎖，耗時 <code>{time_:.2f}</code> 秒。"

        await cli.send_log_message(
            f"✅ #gban #unblock\n{exec_info}\n{short_info}",
            LogTopics.auto,
        )

        ActionLogs.destroy(target.id)

        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                short_info,
                disable_web_page_preview=True,
            )
        )
