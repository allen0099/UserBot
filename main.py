import logging

from bot import Bot

log: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.getLogger("pyrogram").setLevel(logging.WARNING)

if __name__ == '__main__':
    user_bot: Bot = Bot()
    user_bot.run()
