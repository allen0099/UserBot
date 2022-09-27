import logging
import sys
from typing import Union

import pyrogram
from pyrogram import Client, types
from pyrogram.errors import ApiIdInvalid
from pyrogram.session import Session

from core import settings
from core.log import main_logger

log: logging.Logger = main_logger(__name__)


class Bot(Client):
    _instance: Union[None, "Bot"] = None

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

        except (ApiIdInvalid, AttributeError):
            log.critical("[Bot] Api ID is invalid")
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
