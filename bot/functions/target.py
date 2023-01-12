from pyrogram import Client, errors, types

from bot.errors import BotError


def is_protected(target: types.User | types.Chat) -> bool:
    if getattr(target, "is_verified", False):
        return True

    if getattr(target, "is_support", False):
        return True

    if getattr(target, "is_self", False):
        return True

    from database.models.users import Users

    u: Users = Users.get(target.id)

    if u.is_white():
        return True

    return False


async def get_command_target(
    cli: Client, msg: types.Message
) -> types.User | types.Chat:
    target: types.User | types.Chat | None = None
    t: int | str = msg.command[1]

    if t.startswith("https://t.me/"):
        t = t[13:]

    try:
        target = await cli.get_users(t)

    except (errors.PeerIdInvalid, errors.UsernameNotOccupied, IndexError):
        pass

    if not target:
        try:
            target = await cli.get_chat(t)

        except (errors.PeerIdInvalid, errors.UsernameNotOccupied):
            raise BotError("找不到對象")

    return target


async def get_forward_target(msg: types.Message) -> types.User | types.Chat | None:
    """
    Get target from forward.

    Args:
        msg:

    Returns:

    """
    target: types.User | types.Chat | None = None

    if msg.reply_to_message:
        if msg.reply_to_message.forward_from or msg.reply_to_message.forward_from_chat:
            target = (
                msg.reply_to_message.forward_from
                or msg.reply_to_message.forward_from_chat
            )

    return target


async def get_target(cli: Client, msg: types.Message) -> types.User | types.Chat:
    """
    Get target from reply or command.

    Args:
        cli:
        msg:

    Returns:

    """
    target: types.User | types.Chat | None = None

    if msg.reply_to_message:
        target = msg.reply_to_message.from_user or msg.reply_to_message.sender_chat

    if len(msg.command) > 1:
        target = await get_command_target(cli, msg)

    if not target:
        raise BotError("沒有指定對象")

    return target
