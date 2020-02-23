import logging
import platform

from pyrogram import Client
from pyrogram.session import Session

log: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.getLogger("pyrogram").setLevel(logging.WARNING)

if __name__ == '__main__':
    app: Client = Client(
        "bot",
        app_version="Elegant 0.0.0.0",
        device_model=platform.node(),
        system_version=platform.system() + " " + platform.release()
    )

    try:
        Session.notice_displayed = True
        app.start()
        log.debug("Client started successfully")
        app.idle()
        app.stop()
    except:
        log.critical("Client did not started successfully!")
