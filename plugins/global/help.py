import html
import logging

from pyrogram import Client, filters
from pyrogram.types import Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("help", prefixes="!") & filters.me)
async def help_commands(_: Client, msg: Message):
    text: str = "<b><u>AllenUserBot available commands</u></b>\n" \
                "\n" \
                "<b><u>Available commands:</u></b>\n"
    text += commands("bail", "Release users from kicked list or restrict list in this group")
    text += commands("ban", "Ban a user from a group")
    text += commands("count ", "Return counts of each types chat")
    text += commands("get  ", "Reply a message to get the basic info about any string")
    text += commands("help ", "Show help message, you are looking this")
    text += commands("info  ", "Show version and basic info about bot")
    text += commands("killda", "Clear deleted accounts in this group")
    text += commands("@admin ", "Mention all admins in this group")
    text += commands("mute", "Mute a user from a group")
    text += commands("ping", "Response pong!")
    text += commands("raw", "Return raw info about replied text")
    text += commands("req", "Get a user/group/channel 's basic info")
    text += commands("random", "Roll a six-sided die, or give me something")
    text += commands("zh", "Translate text to Simplified Chinese")
    await msg.reply_text(text)


def commands(command: str, description: str) -> str:
    return f"<code>  {html.escape(command).ljust(10)}{html.escape(description)}</code>\n"
