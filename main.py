import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from bot import Bot

log: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.getLogger("pyrogram").setLevel(logging.WARNING)

load_dotenv(dotenv_path=str(Path(sys.argv[0]).parent / ".env"), verbose=True)

if __name__ == '__main__':
    user_bot: Bot = Bot()
    user_bot.run()
