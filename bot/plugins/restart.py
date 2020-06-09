import logging

from pyrogram import Client, Message, Filters

from bot.functions import restart

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("restart", prefixes="$") & Filters.me)
def _restart(cli: Client, msg: Message) -> None:
    restart(cli)
    log.debug("Restarted successfully!")
