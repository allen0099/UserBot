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


async def get_target(cli: Client, msg: types.Message) -> types.User | types.Chat:
    target: types.User | types.Chat | None = None

    if msg.reply_to_message:
        # 代表有回復的對象，表示要對回復的對象進行全域封鎖
        if msg.reply_to_message.forward_from:
            # 有 forward 先抓 forward
            target = (
                msg.reply_to_message.forward_from
                or msg.reply_to_message.forward_from_chat
            )

        if not target:
            # 抓不到 forward 就抓 reply
            target = msg.reply_to_message.from_user or msg.reply_to_message.sender_chat

    if len(msg.command) > 1:
        target = await get_command_target(cli, msg)

    if not target:
        raise BotError("沒有指定對象")

    return target
