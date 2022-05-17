import asyncio
import logging
import os
import time

from pyrogram import Client, filters, types

from database.blacklist_domain import BlackListDomain

log: logging.Logger = logging.getLogger(__name__)
SLEEP_TIME: int = int(os.getenv("SLEEP_TIME"))


class ACTIONS:
    ADD = "add"
    LIST = "list"
    REMOVE = "remove"


ACTION_LIST: list = [
    ACTIONS.ADD,
    ACTIONS.LIST,
    ACTIONS.REMOVE,
]


@Client.on_message(filters.command("domain", prefixes="!") & filters.me & ~ filters.forwarded)
async def domain(cli: Client, msg: types.Message) -> None:
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
        domain_name: str = commands[2]
        log.debug(f"Adding domain {domain_name}")
        BlackListDomain.add(domain_name)
        response: str = f"Domain {domain_name} added to blacklist"

    elif action == ACTIONS.LIST:
        domain_list: list[str] = BlackListDomain.get_list()
        response: str = f"Blacklisted domains: \n"
        for _ in domain_list:
            response += f"<code>{_}</code>\n"

    elif action == ACTIONS.REMOVE:
        domain_name: str = commands[2]
        log.debug(f"Removing domain {domain_name}")
        BlackListDomain.destroy(domain_name)
        response: str = f"Domain {domain_name} removed from blacklist"

    else:
        return

    time_ = time.perf_counter() - start_time

    m: types.Message = await cli.send_message(msg.chat.id, response + f"\nTook {time_:.2f} seconds.")
    await asyncio.sleep(SLEEP_TIME)
    await m.delete()
