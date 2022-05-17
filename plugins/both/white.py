import asyncio
import html
import logging
import os
import time
from typing import Optional

from pyrogram import Client, filters, types

from database.users import User
from plugins.utils import get_target

log: logging.Logger = logging.getLogger(__name__)
SLEEP_TIME: int = int(os.getenv("SLEEP_TIME"))
STR_PROTECT: str = "protect"
STR_WHITE: str = "white"


class ACTIONS:
    ADD = "add"
    ADD_ALL = "add_all"
    REMOVE = "remove"


ACTION_LIST: list = [
    ACTIONS.ADD,
    ACTIONS.ADD_ALL,
    ACTIONS.REMOVE,
]


def target_check(target: types.User) -> bool:
    if not target:
        return False

    if target.is_deleted:
        return False

    if target.is_bot:
        return False

    return True


def action_choice(action_type: str, action: str, user: User):
    if action_type == STR_WHITE:
        if action in [ACTIONS.ADD, ACTIONS.ADD_ALL]:
            user.set_white()
        elif action == ACTIONS.REMOVE:
            user.set_null()
    elif action_type == STR_PROTECT:
        if action in [ACTIONS.ADD, ACTIONS.ADD_ALL]:
            user.set_protect()
        elif action == ACTIONS.REMOVE:
            user.set_null()


@Client.on_message(filters.command([STR_WHITE, STR_PROTECT], prefixes="!") & filters.me & ~ filters.forwarded)
async def white(cli: Client, msg: types.Message) -> None:
    await msg.delete()
    commands = msg.command

    if len(commands) not in [2, 3]:
        return

    start_time = time.perf_counter()

    action: str = commands[1]
    if action not in ACTION_LIST:
        return

    # Actions
    if action == ACTIONS.ADD:
        target: Optional[types.User] = await get_target(cli, msg, 2)
        if target_check(target):
            u: User = User.get_or_create(target.id)
            action_choice(commands[0], action, u)

            response: str = f"{html.escape(target.first_name)} is now in the {commands[0]} list."
        else:
            response = f"Not added, because {target.id} is a bot or deleted."

    elif action == ACTIONS.ADD_ALL:
        async for member in msg.chat.get_members():
            target: types.User = member.user
            if target_check(target):
                u: User = User.get_or_create(target.id)
                action_choice(commands[0], action, u)

        response: str = f"Added group {msg.chat.title} members to the {commands[0]} list."

    elif action == ACTIONS.REMOVE:
        target: Optional[types.User] = await get_target(cli, msg, 2)
        if target_check(target):
            u: User = User.get_or_create(target.id)
            action_choice(commands[0], action, u)

            response: str = f"{html.escape(target.first_name)} is now removed from the {commands[0]} list."
        else:
            response = f"{target.id} is a bot or deleted."

    else:
        return

    time_ = time.perf_counter() - start_time

    m: types.Message = await cli.send_message(msg.chat.id, response + f"\nTook {time_:.2f} seconds.")
    await asyncio.sleep(SLEEP_TIME)
    await m.delete()
