import logging

from bot import Bot

log: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.getLogger("pyrogram").setLevel(logging.WARNING)

if __name__ == '__main__':
    user_bot: Bot = Bot()
    user_bot.init()
    user_bot.run()


    # Catch stop signal
    def handler(signal_received, frame):
        log.debug("SIGINT or CTRL-C detected.")
        user_bot.stop()
        exit(0)

    # TODO 想不到怎麼處理比較好，用迴圈會炸掉 CPU 使用率，不過可以完美的結束程式
    # import signal
    # while True:
    #     signal.signal(signal.SIGINT, handler)
