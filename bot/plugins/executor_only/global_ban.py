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
    await msg.delete()

    start_time: float = time.perf_counter()

    target: types.User | types.Chat = await get_target(cli, msg)

    if is_protected(target):
        await cli.send_log_message(
            f"❌ #gban\n"
            f"{msg.from_user.mention} 試圖在 <code>{msg.chat.id}</code> 對 "
            f"<code>{target.id}</code> 執行全域封鎖，"
            f"但因為 <code>{target.id}</code> 在保護清單中，因此操作失敗。",
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
    u.level = PermissionLevel.BLACK
    u.add()

    if isinstance(target, types.User):
        counter: int = 0
        common_chats: list[types.Chat] = await target.get_common_chats()
        groups: list[int] = Privilege.admin_group_list()
        ban_message: str = f"已將 {target.mention} 從下列群組中封鎖：\n"

        for chat in common_chats:
            if chat.id in groups:
                counter += 1

                ban_message += f"{get_chat_link(chat)}\n"
                ActionLogs.create_user_gban_log(target.id, chat.id, msg.from_user.id)
                # await cli.ban_chat_member(chat.id, target.id)
                # await cli.delete_user_history(chat.id, target.id)

        time_: float = time.perf_counter() - start_time

        await cli.send_log_message(
            f"✅ #gban\n"
            f"{msg.from_user.mention} 在 <code>{msg.chat.id}</code> 執行了全域封鎖，"
            f"{ban_message}\n"
            f"共封鎖了 <code>{counter}</code> 個群組，耗時 <code>{time_:.2f}</code> 秒。",
            LogTopics.auto,
        )

        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                f"共封鎖了 <code>{counter}</code> 個群組，耗時 <code>{time_:.2f}</code> 秒。",
                disable_web_page_preview=True,
            )
        )

    else:
        time_: float = time.perf_counter() - start_time
        ActionLogs.create_chat_gban_log(target.id, msg.from_user.id)

        await cli.send_log_message(
            f"✅ #gban #chat\n"
            f"{msg.from_user.mention} 在 <code>{msg.chat.id}</code> 執行了全域封鎖，"
            f"封鎖了 {get_chat_link(target)}，耗時 <code>{time_:.2f}</code> 秒。",
            LogTopics.auto,
        )

        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                f"封鎖了 {get_chat_link(target)}，耗時 <code>{time_:.2f}</code> 秒。",
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
    await msg.delete()
    # TODO: Implement undo global ban
