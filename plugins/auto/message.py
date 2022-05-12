import asyncio
import html
import logging
import os
from datetime import datetime, timedelta

from pyrogram import Client, filters, types
from pyrogram.enums import MessageEntityType

from database.gbanlog import GBanLog
from plugins.utils import from_admin_groups, from_anonymous, from_bot, from_whitelist_user, get_entity_string

log: logging.Logger = logging.getLogger(__name__)
LOG_CHANNEL: str = os.getenv("LOG_CHANNEL")
TIME_DELTA: timedelta = timedelta(days=-int(os.getenv("TIME_DELTA")))
COUNTER_LIMIT: int = int(os.getenv("COUNTER_LIMIT"))
SLEEP_TIME: int = int(os.getenv("SLEEP_TIME"))


def is_check(msg: types.Message) -> bool:
    if from_anonymous(msg):
        return False

    if not from_admin_groups(msg):
        return False

    if from_bot(msg):
        return False

    if from_whitelist_user(msg):
        return False

    return True


async def is_user_too_young(msg: types.Message) -> bool:
    """
    Check if the user joined the chat before the challenge period

    Args:
        msg:

    Returns:
        bool: True if the user joined the chat after the challenge period
    """
    user: types.ChatMember = await msg.chat.get_member(msg.from_user.id)
    challenge_days = datetime.now() + TIME_DELTA

    log.debug(f"{msg.from_user.id} joined at {user.joined_date}")

    if user.joined_date > challenge_days:
        return True

    return False


async def is_user_too_quite(cli: Client, msg: types.Message) -> bool:
    """
    Check if the user has a message count below the limit

    Args:
        cli:
        msg:

    Returns:
        bool: True if the user says too little
    """
    counter: int = await cli.search_messages_count(msg.chat.id, from_user=msg.from_user.id)

    log.debug(f"{msg.from_user.id} has {counter} messages in {msg.chat.id}")

    if counter <= COUNTER_LIMIT:
        return True

    return False


async def webpage_check(cli: Client, msg: types.Message):
    if msg.web_page.type in ["telegram_user", "telegram_bot", "telegram_channel", "telegram_megagroup"]:
        log.debug(f"{msg.from_user.id} sent a Telegram webpage to {msg.chat.id}")
        if await is_user_too_quite(cli, msg):
            if await is_user_too_young(msg):
                log.debug(f"{msg.from_user.id} is sending spam messages")
                warnings: types.Message = await msg.reply_text(
                    "Your account is banned for spamming.\n"
                    "If you think this is a mistake, please contact me in https://t.me/PMallen0099",
                    disable_web_page_preview=True
                )

                await asyncio.sleep(SLEEP_TIME)
                GBanLog.create(msg.from_user.id, msg.chat.id)
                await cli.ban_chat_member(msg.chat.id, msg.from_user.id)

                # clean up
                await cli.delete_user_history(msg.chat.id, msg.from_user.id)
                await warnings.delete()

                await cli.send_message(
                    LOG_CHANNEL,
                    f"#userbot \n"
                    f"<code>{msg.from_user.id}</code> in "
                    f"<code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>) "
                    f"has been banned for spamming."
                )
    else:
        log.debug(f"{msg.web_page}")


@Client.on_message(filters.group, group=-100)
@Client.on_edited_message(filters.group, group=-100)
async def message(cli: Client, msg: types.Message) -> None:
    """
    Do message check
    """
    if not is_check(msg):
        return

    if msg.web_page:
        await webpage_check(cli, msg)
        return

    if msg.entities:
        url_types: list = [MessageEntityType.URL, MessageEntityType.TEXT_LINK]
        mention_types: list = [MessageEntityType.MENTION, MessageEntityType.TEXT_MENTION]

        for entity in msg.entities:
            if entity.type in url_types + mention_types:
                log.debug(f"Entity text in {msg.chat.title}: {get_entity_string(msg.text, entity)}")

            # URLS
            if entity.type in url_types:
                if entity.type == MessageEntityType.TEXT_LINK:
                    log.debug(f"{msg.from_user.id} sends a link, url: {entity.url}")
                else:
                    log.debug(f"{msg.from_user.id} sends a url.")

            # mentions
            elif entity.type in mention_types:
                if entity.type == MessageEntityType.TEXT_MENTION:
                    log.debug(f"{msg.from_user.id} mentions someone, id: {entity.user.id}")
                else:
                    log.debug(f"{msg.from_user.id} mentions someone.")
