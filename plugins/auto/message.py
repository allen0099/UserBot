import asyncio
import html
import logging
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse

from pyrogram import Client, errors, filters, types
from pyrogram.enums import MessageEntityType

from database.blacklist_domain import BlackListDomain
from database.gbanlog import GBanLog
from database.users import User
from plugins.utils import get_entity_string, is_admin_group, is_protect_list_user, is_white_list_user

log: logging.Logger = logging.getLogger(__name__)
LOG_CHANNEL: str = os.getenv("LOG_CHANNEL")
TIME_DELTA: timedelta = timedelta(days=-int(os.getenv("TIME_DELTA")))
LOWER_LIMIT: int = int(os.getenv("LOWER_LIMIT"))
COUNTER_LIMIT: int = int(os.getenv("COUNTER_LIMIT"))
SLEEP_TIME: int = int(os.getenv("SLEEP_TIME"))

WARNINGS: str = f"Your account is banned for spamming.\n" \
                f"If you think this is a mistake, please contact me in https://t.me/PMallen0099\n" \
                f"<b><u>DO NOT PM me, I will not reply any pm.</u></b>"


def is_check(msg: types.Message) -> bool:
    if not is_admin_group(msg.chat):
        return False

    if msg.sender_chat:
        return False

    if msg.from_user.is_bot:
        return False

    if is_white_list_user(msg.from_user):
        return False

    if is_protect_list_user(msg.from_user):
        return False

    return True


async def is_user_too_young(cli: Client, msg: types.Message) -> bool:
    """
    Check if the user joined the chat before the challenge period

    Args:
        cli:
        msg:

    Returns:
        bool: True if the user joined the chat after the challenge period
    """
    try:
        user: types.ChatMember = await msg.chat.get_member(msg.from_user.id)
    except errors.UserNotParticipant:
        # User is sending message without joining the chat
        await clean_up(cli, msg, f"#userbot #ban #counter\n"
                                 f"From: {msg.from_user.id}\n"
                                 f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
                                 f"Reason: User sent a message without joining the chat\n"
                                 f"Message Link: {msg.link}")
        return False
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
    try:
        counter: int = await cli.search_messages_count(msg.chat.id, from_user=msg.from_user.id)
    except errors.PeerIdInvalid:
        # TODO handle this error
        return False

    log.debug(f"{msg.from_user.id} has {counter} messages in {msg.chat.id} ({msg.chat.title})")

    if counter > LOWER_LIMIT:
        user: User = User.get_or_create(msg.from_user.id)
        user.set_protect()
        log.debug(f"{msg.from_user.id} is now protected")
        return False

    if counter <= COUNTER_LIMIT:
        return True

    return False


async def clean_up(cli: Client, msg: types.Message, log_message: str) -> None:
    log.debug(f"Executing clean up for {msg.from_user.id} in {msg.chat.title}")
    warnings: types.Message = await msg.reply_text(
        WARNINGS,
        disable_web_page_preview=True,
    )

    await asyncio.sleep(SLEEP_TIME)
    GBanLog.create(msg.from_user.id, msg.chat.id)
    await cli.ban_chat_member(msg.chat.id, msg.from_user.id)

    # clean up
    await cli.delete_user_history(msg.chat.id, msg.from_user.id)
    await warnings.delete()

    await cli.send_message(
        LOG_CHANNEL,
        log_message,
        disable_web_page_preview=True,
    )


async def check_webpage(cli: Client, msg: types.Message) -> None:
    if msg.web_page.type in ["telegram_user", "telegram_bot", "telegram_channel", "telegram_megagroup"]:
        await clean_up(cli, msg, f"#userbot #ban #webpage #telegram\n"
                                 f"From: <code>{msg.from_user.id}</code>\n"
                                 f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
                                 f"Reason: Telegram webpage spam\n"
                                 f"Message Link: {msg.link}")
        return

    else:
        if domain_in_black(msg.web_page.url):
            url: str = url_encode(msg.web_page.url)
            await clean_up(cli, msg, f"#userbot #ban #webpage\n"
                                     f"From: <code>{msg.from_user.id}</code>\n"
                                     f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
                                     f"URL: <code>{url}</code>\n"
                                     f"Message Link: {msg.link}")
            return

        await cli.send_message(
            LOG_CHANNEL,
            f"#userbot #log #webpage\n"
            f"From: <code>{msg.from_user.id}</code>\n"
            f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
            f"URL: <code>{msg.web_page.url}</code>\n"
            f"Message Link: {msg.link}",
            disable_web_page_preview=True,
        )
        return


def url_encode(url: str) -> str:
    if len(url) > 20:
        match_len: int = len(url) - 20
        url = url[:15] + match_len * "x" + url[-5:]
        return url
    return url


def domain_in_black(url: str) -> bool:
    parsed_url: urlparse = urlparse(url)
    log.debug(f"Parsed URL: {parsed_url}")
    if parsed_url.netloc in BlackListDomain.get_list():
        return True
    return False


async def entity_url_checker(cli: Client, msg: types.Message, entity: types.MessageEntity) -> bool:
    if entity.type == MessageEntityType.TEXT_LINK:
        url: str = entity.url
    else:
        url: str = get_entity_string(msg.text, entity)
    log.debug(f"{msg.from_user.id} sent a URL to {msg.chat.title}, link: {url}")

    if not url.startswith("http"):
        url: str = f"https://{url}"

    if domain_in_black(url):
        url = url_encode(url)
        await clean_up(cli, msg, f"#userbot #ban #entity #url\n"
                                 f"From: <code>{msg.from_user.id}</code>\n"
                                 f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
                                 f"URL: <code>{url}</code>\n"
                                 f"Message Link: {msg.link}")
        return True

    await cli.send_message(
        LOG_CHANNEL,
        f"#userbot #log #entity #url\n"
        f"From: <code>{msg.from_user.id}</code>\n"
        f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
        f"URL: <code>{url}</code>\n"
        f"Message Link: {msg.link}",
        disable_web_page_preview=True,
    )
    return False


async def entity_mention_checker(cli: Client, msg: types.Message, entity: types.MessageEntity) -> bool:
    user: types.User = entity.user

    if not user:
        try:
            user = await cli.get_users(get_entity_string(msg.text, entity))
        except errors.PeerIdInvalid:
            # Maybe a supergroup, or channel?
            await cli.send_message(
                LOG_CHANNEL,
                f"#userbot #log #mention\n"
                f"From: <code>{msg.from_user.id}</code>\n"
                f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
                f"Mention: <code>{get_entity_string(msg.text, entity)}</code>\n"
                f"Message Link: {msg.link}",
                disable_web_page_preview=True,
            )
            return False

    if entity.type == MessageEntityType.TEXT_MENTION:
        log.debug(f"{msg.from_user.id} mentions someone, id: {entity.user.id}")
    else:
        log.debug(f"{msg.from_user.id} mentions someone.")

    try:
        _check: types.ChatMember = await msg.chat.get_member(user.id)
    except errors.UserNotParticipant:
        # Mentioned a user not in chat or joined chat.
        await clean_up(cli, msg, f"#userbot #ban #mention\n"
                                 f"From: <code>{msg.from_user.id}</code>\n"
                                 f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
                                 f"Mentioned: <code>{user.id}</code>, {get_entity_string(msg.text, entity)}\n"
                                 f"Message Link: {msg.link}")
        return True

    await cli.send_message(
        LOG_CHANNEL,
        f"#userbot #log #mention\n"
        f"From: <code>{msg.from_user.id}</code>\n"
        f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
        f"Mentioned: <code>{user.id}</code>, {get_entity_string(msg.text, entity)}\n"
        f"Status: <code>{_check.status}</code>\n"
        f"Message Link: {msg.link}",
        disable_web_page_preview=True,
    )
    return False


async def check_entities(cli: Client, msg: types.Message) -> None:
    url_types: list = [MessageEntityType.URL, MessageEntityType.TEXT_LINK]
    mention_types: list = [MessageEntityType.MENTION, MessageEntityType.TEXT_MENTION]

    for entity in msg.entities:
        if entity.type in url_types + mention_types:
            log.debug(f"Entity text in {msg.chat.title}: {get_entity_string(msg.text, entity)}")

        if entity.type in url_types:
            if await entity_url_checker(cli, msg, entity):
                return

        elif entity.type in mention_types:
            if await entity_mention_checker(cli, msg, entity):
                return


async def check_edit(cli: Client, msg: types.Message) -> bool:
    await clean_up(cli, msg, f"#userbot #ban #edit\n"
                             f"From: <code>{msg.from_user.id}</code>\n"
                             f"In: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
                             f"Message Link: {msg.link}")

    return True


@Client.on_message(filters.group, group=-100)
@Client.on_edited_message(filters.group, group=-100)
async def message(cli: Client, msg: types.Message) -> None:
    """
    Do message check
    """
    if not is_check(msg):
        return

    if msg.edit_date:
        if await is_user_too_quite(cli, msg):
            if await is_user_too_young(cli, msg):
                log.debug(f"{msg.from_user.id} is too young to edit messages.")
                if await check_edit(cli, msg):
                    return

    if msg.web_page:
        if await is_user_too_quite(cli, msg):
            if await is_user_too_young(cli, msg):
                log.debug(f"{msg.from_user.id} sent a webpage and should check at {msg.chat.title}")
                await check_webpage(cli, msg)
                return

    if msg.entities:
        if await is_user_too_quite(cli, msg):
            if await is_user_too_young(cli, msg):
                log.debug(f"{msg.from_user.id} should check entities in {msg.chat.title}")
                await check_entities(cli, msg)
                return
