import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from bot import Bot
from database import Database

load_dotenv(dotenv_path=str(Path(sys.argv[0]).parent / ".env"), verbose=True)

log: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=eval(f"logging.{os.getenv('LOG_LEVEL')}"),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.getLogger("pyrogram").setLevel(logging.WARNING)

db: Database = Database()

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        cmd: str = sys.argv[1]
        if cmd == 'rebuild':
            db.rebuild()

    user_bot: Bot = Bot()
    user_bot.run()
