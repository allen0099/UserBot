import logging

from pyrogram import types

from database.privilege import Privilege
from database.users import User

log: logging.Logger = logging.getLogger(__name__)


def from_anonymous(msg: types.Message) -> bool:
    """
    Checks if the user is anonymous.

    Args:
        msg:

    Returns:
        bool: True if the user is anonymous, False otherwise.
    """
    return True if msg.sender_chat else False


def from_whitelist_user(msg: types.Message) -> bool:
    """
    Checks if the user is whitelisted.

    Args:
        msg:

    Returns:
        bool: True if the user is whitelisted, False otherwise.
    """
    if msg.from_user.id in User.get_whitelist():
        return True

    return False


def from_bot(msg: types.Message) -> bool:
    """
    Checks if the message is sent from a bot.

    Args:
        msg:

    Returns:
        bool: True if the message is sent from a bot, False otherwise.
    """
    return True if msg.from_user.is_bot else False


def from_contact(msg: types.Message) -> bool:
    """
    Checks if the message is sent from a contact.

    Args:
        msg:

    Returns:
        bool: True if the message is sent from a contact, False otherwise.
    """
    return True if msg.from_user.is_contact else False


def from_admin_groups(msg: types.Message) -> bool:
    """
    Checks if the message is sent from admin group.

    Args:
        msg:

    Returns:
        bool: True if the message is sent from admin group, False otherwise.
    """
    if msg.chat.id in Privilege.admin_groups():
        return True

    return False


def is_white_list_user(user: types.User) -> bool:
    """
    Checks if the user is whitelisted.

    Args:
        user:

    Returns:
        bool: True if the user is whitelisted, False otherwise.
    """
    if user.id in User.get_whitelist():
        return True

    return False


def is_black_listed_user(user: types.User) -> bool:
    """
    Checks if the user is blacklisted.

    Args:
        user:

    Returns:
        bool: True if the user is blacklisted, False otherwise.
    """
    if user.id in User.get_blacklist():
        return True

    return False


def permission_check(msg: types.Message) -> bool:
    if from_anonymous(msg):
        log.debug(f"Sender chat {msg.sender_chat.title} is not allowed, skipping command.")
        return False

    if not from_whitelist_user(msg):
        log.debug(f"User {msg.from_user.id} is not whitelisted, skipping command.")
        return False

    return True


def get_entity_string(text: str, entity: types.MessageEntity) -> str:
    """
    Parse the entity from the text.

    Args:
        text:
        entity:

    Returns:
        str: Parsed string.
    """
    utf_16_text: bytes = text.encode('utf-16')
    start_offset: int = entity.offset * 2 + 2
    length: int = entity.length * 2
    return utf_16_text[start_offset:start_offset + length].decode('utf-16')
