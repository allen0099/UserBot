import asyncio
import logging
import os
import time
from typing import Optional

from pyrogram import Client, filters, types
from pyrogram.types import Message

from database.gbanlog import GBanLog
from database.privilege import Privilege
from database.users import User
from plugins.utils import get_target, is_protect_list_user, is_white_list_user

log: logging.Logger = logging.getLogger(__name__)
SLEEP_TIME: int = 10
LOG_CHANNEL: str = os.getenv("LOG_CHANNEL")


def permission_check(msg: types.Message) -> bool:
    if msg.sender_chat:
        return False

    if not is_white_list_user(msg.from_user):
        return False

    return True


def target_check(target: Optional[types.User]) -> bool:
    if not target:
        return False

    if is_white_list_user(target):
        return False

    if is_protect_list_user(target):
        return False

    return True


@Client.on_message(filters.command("gban", prefixes="!") & ~ filters.forwarded)
async def global_ban(cli: Client, msg: Message) -> None:
    """
    Globally bans a user from all groups if I have the permission to do so.

    Usage: ``!gban <username/uid>`` or  ``!gban`` by reply
    """
    await msg.delete()

    start_time = time.perf_counter()

    if not permission_check(msg):
        return

    target: Optional[types.User] = await get_target(cli, msg)
    groups: list[int] = Privilege.admin_groups()
    log.debug(f"{msg.from_user.id} is trying to global ban {target.id} in {msg.chat.id}")

    if not target_check(target):
        return

    counter: int = 0
    common_chats: list[types.Chat] = await target.get_common_chats()
    u: User = User.get_or_create(target.id)
    u.set_black()
    for chat in common_chats:
        if chat.id in groups:
            counter += 1
            log.debug(f"Ban user {target.first_name}({target.id}) from {chat.title}({chat.id})")

            GBanLog.create(target.id, chat.id)
            await cli.ban_chat_member(chat.id, target.id)
            await cli.delete_user_history(chat.id, target.id)

    time_ = time.perf_counter() - start_time

    end: Message = await cli.send_message(msg.chat.id, f"Globally banned "
                                                       f"<a href='tg://user?id={target.id}'>"
                                                       f"{target.id}"
                                                       f"</a> "
                                                       f"from <u>{counter}/{len(groups)}</u> groups "
                                                       f"in <u>{time_:.2f}</u> seconds.")
    await cli.send_message(LOG_CHANNEL, f"#userbot #gban\n"
                                        f"Executed by: <a href='tg://user?id={msg.from_user.id}'>"
                                        f"{msg.from_user.first_name}"
                                        f"</a>\n"
                                        f"Target: <a href='tg://user?id={target.id}'>"
                                        f"{target.id}"
                                        f"</a>\n"
                                        f"Groups: <u>{counter}/{len(groups)}</u>\n"
                                        f"Time: <u>{time_:.2f}</u> seconds\n",
                           disable_web_page_preview=True, )

    await asyncio.sleep(SLEEP_TIME)
    await end.delete()


@Client.on_message(filters.command("ungban", prefixes="!") & ~ filters.forwarded)
async def undo_global_ban(cli: Client, msg: Message) -> None:
    """
    Unban a user from all the groups where I am the admin, check if the user is banned from me.

    Usage: ``!ungban <username/uid>`` or  ``!ungban`` by reply
    """
    await msg.delete()

    start_time = time.perf_counter()

    if not permission_check(msg):
        return

    target: Optional[types.User] = await get_target(cli, msg)

    if not target:
        await cli.send_message(msg.chat.id, "No target specified.")
        return

    u = User.get_or_create(target.id)
    u.set_null()
    groups = GBanLog.get_banned_by_id(target.id)

    for chat in groups:
        log.debug(f"Unban user {target.first_name}({target.id}) from {chat}")
        await cli.unban_chat_member(chat, target.id)

    GBanLog.destroy(target.id)

    time_ = time.perf_counter() - start_time

    end: Message = await cli.send_message(msg.chat.id, f"Globally unbanned "
                                                       f"<a href='tg://user?id={target.id}'>"
                                                       f"{target.id}"
                                                       f"</a> "
                                                       f"from <u>{len(groups)}</u> groups "
                                                       f"in <u>{time_:.2f}</u> seconds.")

    await asyncio.sleep(SLEEP_TIME)
    await end.delete()
