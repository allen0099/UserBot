import asyncio
import logging
import os
import platform
import sys
from asyncio import AbstractEventLoop
from datetime import datetime
from typing import Optional, Union

import psutil
from pyrogram import Client
from pyrogram.errors import ApiIdInvalid, AuthKeyUnregistered
from pyrogram.session import Session
from pyrogram.types import User

log: logging.Logger = logging.getLogger(__name__)
__version__: str = "1.0.1"


class Bot:
    _instance: Union[None, "Bot"] = None

    me: Optional[User] = None
    version: str = __version__
    device_model: str = f"PC {platform.architecture()[0]}"
    system_version: str = f"{platform.system()} {platform.python_implementation()} {platform.python_version()}"

    def __init__(self):
        self.app: Client = Client(
            "bot",
            app_version=self.version,
            device_model=self.device_model,
            api_id=os.getenv("API_ID"),
            api_hash=os.getenv("API_HASH"),
            plugins=None,
            system_version=self.system_version
        )

        self.start_time: datetime = datetime.utcnow()
        self.process = psutil.Process(os.getpid())

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def run(self):
        loop: AbstractEventLoop = asyncio.get_event_loop()
        run = loop.run_until_complete
        run(self.run_once())

        self.app.plugins = {
            "enabled": True,
            "root": "plugins",
            "include": [],
            "exclude": []
        }

        log.info("Plugins loaded!")
        self.app.run()

    async def run_once(self):
        # Disable notice
        Session.notice_displayed = True
        logging.getLogger("pyrogram").setLevel(logging.WARNING)

        try:
            await self.app.start()

        except (ApiIdInvalid, AttributeError):
            log.critical("[Failed] Api ID is invalid")
            sys.exit(1)

        except AuthKeyUnregistered:
            log.critical("[Oops!] Session expired!")
            log.critical("        Removed old session and exit...!")
            await self.app.storage.delete()
            exit(1)

        try:
            me: User = await self.app.get_me()

            info_str: str = f"[Bot] {me.first_name}"
            info_str += f" {me.last_name}" if me.last_name else ""
            info_str += f" (@{me.username})" if me.username else ""
            info_str += f" ID: {me.id}"

            log.info(info_str)

            self.me: User = me

        except Exception as e:
            log.exception(e)
            sys.exit(1)

        log.info("Client started successfully")

        await self.app.stop()
        logging.getLogger("pyrogram").setLevel(logging.INFO)
