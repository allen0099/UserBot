import logging
import platform
import sys

from pyrogram import Client
from pyrogram.errors import ApiIdInvalid
from pyrogram.session import Session
from pyrogram.types import User

log: logging.Logger = logging.getLogger(__name__)


class Bot:
    def __init__(self):
        self.app_version: str = "0.1.0"
        self.device_model: str = f"PC {platform.architecture()[0]}"
        self.system_version: str = f"{platform.system()} {platform.python_implementation()} {platform.python_version()}"

        self.app: Client = Client(
            "bot",
            app_version=self.app_version,
            device_model=self.device_model,
            system_version=self.system_version
        )

    def run(self):
        self.app.run(self.run_once())
        self.app.run()

    async def run_once(self):
        # Disable notice
        Session.notice_displayed = True
        logging.getLogger("pyrogram.client").disabled = True
        await self.app.start()
        logging.getLogger("pyrogram.client").disabled = False

        try:
            me: User = await self.app.get_me()

            info_str: str = f"[Loaded] {me.first_name}"
            info_str += f" {me.last_name}" if me.last_name is not None else ""
            info_str += f" (@{me.username})" if me.username is not None else ""
            info_str += f" ID: {me.id}"

            log.info(info_str)
        except ApiIdInvalid:
            log.critical("Api ID is invalid")
            sys.exit(1)
        except Exception as e:
            log.exception(e)
            sys.exit(1)

        log.info("Client started successfully")

        await self.app.stop()
