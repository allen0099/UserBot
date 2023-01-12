import logging
import os
import sys
from builtins import function
from typing import Union

import psutil
import pyrogram
from pyrogram import Client, errors, types
from pyrogram.errors import AuthKeyUnregistered
from pyrogram.session import Session

from bot.methods import CustomMethods
from core import settings
from core.log import main_logger

log: logging.Logger = main_logger(__name__)


class Bot(Client, CustomMethods):
    _instance: Union[None, "Bot"] = None
    dealing_message: types.Message | None = None
    current_handler: function | None = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern

        Args:
            *args:
            **kwargs:
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.process: psutil.Process = psutil.Process(os.getpid())

        super().__init__(
            "bot", api_id=settings.TELEGRAM_API_ID, api_hash=settings.TELEGRAM_API_HASH
        )

    def run(self, coroutine=None):
        """Prepare and start the bot normally.

        Args:
            coroutine:

        Returns:

        """
        super().run(self.prepare_start())

        log.debug("Loading plugins...")

        self.plugins = {
            "enabled": True,
            "root": "bot/plugins",
            "include": [],
            "exclude": [],
        }

        log.debug("Plugins loaded!")

        super().run(coroutine)

    async def prepare_start(self):
        """Prepare the bot before starting.

        Returns:

        """
        # Disable Pyrogram notice
        Session.notice_displayed = True

        log.info(f"Initializing pyrogram...")
        log.debug(f"Pyrogram version: {pyrogram.__version__}")

        try:
            await self.start()

        except (errors.ApiIdInvalid, AttributeError):
            log.critical("[Bot] Api ID is invalid")
            sys.exit(1)

        except AuthKeyUnregistered:
            # TODO: implement auto delete session file
            log.critical("[Bot] Delete session file and restart the bot")
            sys.exit(1)

        me: types.User = self.me

        info_str: str = (
            f"{me.first_name}"
            f"{' ' + me.last_name if me.last_name else ''}"
            f"{' (@' + me.username + ')' if me.username else ''}"
            f" ID: {me.id}"
        )

        log.info(info_str)

        log.info("Pyrogram initialized successfully!")

        await self.stop()
