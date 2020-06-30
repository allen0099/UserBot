from pyrogram import Client


def restart(cli: Client) -> None:
    from threading import Thread
    Thread(target=cli.restart).start()
