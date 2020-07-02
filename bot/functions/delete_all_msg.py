import pyrogram
from pyrogram import Client
from pyrogram.api.functions import channels


def delete_all_msg(cli: Client, chat: pyrogram.Chat, on_user: pyrogram.User) -> None:
    cli.send(
        channels.DeleteUserHistory(
            channel=cli.resolve_peer(chat.id),
            user_id=cli.resolve_peer(on_user.id)
        )
    )
