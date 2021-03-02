import logging
import platform
import sys

from pyrogram import Client
from pyrogram.errors import ApiIdInvalid
from pyrogram.session import Session

from _models_old import Base, engine, session

log: logging.Logger = logging.getLogger(__name__)


class Bot:
    def __init__(self):
        self.version: str = "0.1.0"

    def init(self):
        return

    def run(self):
        self.app: Client = Client(
            "bot",
            app_version=f"allen0099's User Bot {self.version}",
            device_model=platform.node(),
            system_version=platform.system() + " " + platform.release()
        )

        # Disable notice
        Session.notice_displayed = True
        self.app.start()

        try:
            me = self.app.get_me()
            log.info(f"[Loaded] {me.first_name} (@{me.username if me.username is not None else ''}) ID: {me.id}")
        except ApiIdInvalid:
            log.critical('Api ID is invalid')
            sys.exit(1)
        except Exception as e:
            log.exception(e)
            sys.exit(1)

        log.info("Client started successfully")

        self.app.stop()
        self.app.run()
