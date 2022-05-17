import logging
from typing import Optional

from pyrogram import Client, enums, errors, types

from database.privilege import Privilege
from database.users import User

log: logging.Logger = logging.getLogger(__name__)


def is_admin_group(group: types.Chat) -> bool:
    """
    Checks if the group is an admin group.

    Args:
        group:

    Returns:
        bool: True if the group is an admin group, False otherwise.
    """
    if group.type != enums.ChatType.SUPERGROUP:
        return False

    if group.id in Privilege.admin_groups():
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


def is_protect_list_user(user: types.User) -> bool:
    """
    Checks if the user is in protect list.

    Args:
        user:

    Returns:
        bool: True if the user is in protect list, False otherwise.
    """
    if user.id in User.get_protected():
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


async def get_target(cli: Client, msg: types.Message, location: int = 1) -> Optional[types.User]:
    target: Optional[types.User] = None

    if msg.reply_to_message:
        target = msg.reply_to_message.from_user
        return target

    try:
        target = await cli.get_users(msg.command[location])
    except (errors.PeerIdInvalid, errors.UsernameNotOccupied):
        return target

    return target


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
