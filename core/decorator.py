"""
Used to decorate functions like logging, rate limiting, etc.
"""
import inspect
import logging
from typing import Optional, Union

from pyrogram import types

from bot import Bot
from core.log import main_logger, event_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


def event_log(func):
    """
    Decorator to print function call details.

    This includes parameters names and effective values.
    Modified from: https://stackoverflow.com/a/6278457
    """

    log.debug(f"Ready to log {func.__module__}.{func.__qualname__} ...")

    async def wrapper(*args, **kwargs):
        func_args: dict[str, object] = (
            inspect.signature(func).bind(*args, **kwargs).arguments
        )

        instance: Optional[Bot] = None
        message: Optional[types.Message] = None

        # Parse args from function passed
        for (name, value) in func_args.items():
            arg_name: str = name
            arg_value: object = value

            if isinstance(arg_value, Bot):
                instance = arg_value

            if isinstance(arg_value, types.Message):
                message = arg_value

        if not message:
            logger.critical(
                f"{func.__module__}.{func.__qualname__} - No message found in {func_args.items()}"
            )

        if message:
            executor: Union[types.Chat, types.User] = (
                message.from_user or message.sender_chat
            )  # From channel or user
            func_name: str = func.__qualname__
            in_chat: types.Chat = message.chat

            if executor:
                logger.debug(
                    f"[Execute] {executor.id} triggered {func_name} in {in_chat.id}"
                )

            else:
                logger.debug(f"[Automatic] Triggered {func_name} in {in_chat.id}")

            logger.debug(f"  Full message: {repr(message)}")

        # Ready to return
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)

        return func(*args, **kwargs)

    return wrapper
