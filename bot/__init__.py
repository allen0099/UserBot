import logging
import os
import platform
import sys
from datetime import datetime

import psutil
from pyrogram import Client
from pyrogram.errors import ApiIdInvalid, AuthKeyUnregistered
from pyrogram.session import Session
from pyrogram.types import User
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

log: logging.Logger = logging.getLogger(__name__)


class Bot:
    app_version: str = "0.1.1"
    device_model: str = f"PC {platform.architecture()[0]}"
    system_version: str = f"{platform.system()} {platform.python_implementation()} {platform.python_version()}"

    def __init__(self):
        self.app: Client = Client(
            "bot",
            app_version=self.app_version,
            device_model=self.device_model,
            system_version=self.system_version
        )

        self.start_time: datetime = datetime.utcnow()
        self.process = psutil.Process(os.getpid())

    def run(self):
        self.app.run(self.run_once())
        self.app.run()

    async def run_once(self):
        # Disable notice
        Session.notice_displayed = True
        logging.getLogger("pyrogram.client").disabled = True
        try:
            await self.app.start()
        except AuthKeyUnregistered:
            log.critical("[Oops!] Session expired!")
            log.critical("        Removed old session and exit...!")
            await self.app.storage.delete()
            exit(1)
        logging.getLogger("pyrogram.client").disabled = False

        try:
            me: User = await self.app.get_me()

            info_str: str = f"[Bot] {me.first_name}"
            info_str += f" {me.last_name}" if me.last_name else ""
            info_str += f" (@{me.username})" if me.username else ""
            info_str += f" ID: {me.id}"

            log.info(info_str)
        except ApiIdInvalid:
            log.critical("[Failed] Api ID is invalid")
            sys.exit(1)
        except Exception as e:
            log.exception(e)
            sys.exit(1)

        try:
            from main import db

            with db.engine.connect() as conn:
                conn.execute(text('SELECT now()'))

            log.info("[Database] Successfully connect!")
        except OperationalError:
            log.critical("[Failed] Can not connect to database!")
            sys.exit(1)
        except Exception as e:
            log.exception(e)
            sys.exit(1)

        log.info("Client started successfully")

        await self.app.stop()
