import logging

from pyrogram import Client, Message, Filters

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.me & Filters.command("c"))
def test(cli: Client, msg: Message) -> None:
    """Empty for copy"""
    log.info("Not implemented")
