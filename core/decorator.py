"""
Used to decorate functions like logging, rate limiting, etc.
"""
import inspect
import logging
from functools import wraps
from typing import Callable, Union

from pyrogram import types

from bot import Bot
from core.log import event_logger, main_logger
from database.models.records import Records

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


async def graceful_return(
    func: Callable, bot: Bot, msg: types.Message, *args, **kwargs
) -> Callable:
    if inspect.iscoroutinefunction(func):
        return await func(bot, msg, *args, **kwargs)

    return func(bot, msg, *args, **kwargs)


def event_log() -> Callable:
    def decorator(func) -> Callable:
        log.debug(f"Ready to log {func.__module__}.{func.__qualname__} ...")

        @wraps(func)
        async def wrapper(bot: Bot, msg: types.Message, *args, **kwargs) -> Callable:
            if bot.current_handler == func and bot.dealing_message == msg:
                return lambda x: log.debug("Message is dealing")

            bot.dealing_message = msg
            bot.current_handler = func

            executor: Union[types.Chat, types.User] = (
                msg.from_user or msg.sender_chat
            )  # From channel or user
            func_name: str = func.__qualname__
            in_chat: types.Chat = msg.chat

            if executor:
                logger.debug(
                    f"[Execute] {executor.id} triggered {func_name} in {in_chat.id}"
                )

            else:
                logger.debug(f"[Automatic] Triggered {func_name} in {in_chat.id}")

            logger.debug(f"  Full message: {repr(msg)}")

            record: Records = Records(executor.id, in_chat.id, func_name, repr(msg))
            record.add()

            return await graceful_return(func, bot, msg, *args, **kwargs)

        return wrapper

    return decorator


def permission_check(permission) -> Callable:
    def decorator(func) -> Callable:
        log.debug(f"Checking {func.__qualname__} at {permission} permission...")

        @wraps(func)
        async def wrapper(bot: Bot, msg: types.Message, *args, **kwargs) -> Callable:
            print("Not implemented yet")

            return await graceful_return(func, bot, msg, *args, **kwargs)

        return wrapper

    return decorator
