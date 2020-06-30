import logging
import platform

from pyrogram import Client
from pyrogram.session import Session

from bot.functions import iter_supergroups
from models import Base, engine, session

log: logging.Logger = logging.getLogger(__name__)


class Bot:
    # Hexlightning style
    def __init__(self):
        self.db: Base = Base
        self.db_engine: engine = engine
        self.session: session = session
        self.version: str = "0.0.2"

    def init(self):
        self.db.metadata.create_all(self.db_engine)

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
            log.info(f"[Loaded] {me.first_name} (@{me.username}) ID: {me.id}")
        except Exception as e:
            log.critical(f"{e}")

        iter_supergroups(self.app)

        log.info("Client started successfully")

    def stop(self):
        self.app.stop()
