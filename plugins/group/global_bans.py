import asyncio
import logging
import time
from typing import Optional

from pyrogram import Client, filters, types
from pyrogram.types import Message

from database.gbanlog import GBanLog
from database.privilege import Privilege
from database.users import User
from plugins.utils import is_white_list_user, permission_check

log: logging.Logger = logging.getLogger(__name__)
SLEEP_TIME: int = 10


async def get_target(cli: Client, msg: Message) -> Optional[types.User]:
    target: Optional[types.User] = None
    if msg.reply_to_message:
        target = msg.reply_to_message.from_user

    if len(msg.command) == 2:
        target = await cli.get_users(msg.command[1])

    return target


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

    if not target:
        await cli.send_message(msg.chat.id, "No target specified.")
        return

    if is_white_list_user(target):
        return

    counter: int = 0
    common_chats: list[types.Chat] = await target.get_common_chats()
    u: User = User.get_or_create(target.id)
    u.set_black()
    for chat in common_chats:
        if chat.id in groups:
            counter += 1
            log.debug(f"Ban user {target.first_name} from {chat.id}")

            GBanLog.create(target.id, chat.id)
            await cli.delete_user_history(chat.id, target.id)
            await cli.ban_chat_member(chat.id, target.id)

    time_ = time.perf_counter() - start_time

    end: Message = await cli.send_message(msg.chat.id, f"Globally banned "
                                                       f"<a href='tg://user?id={target.id}'>"
                                                       f"{target.id}"
                                                       f"</a> "
                                                       f"from <u>{counter}/{len(groups)}</u> groups "
                                                       f"in <u>{time_:.2f}</u> seconds.")

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
        log.debug(f"Unban user {target.first_name} from {chat}")
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
