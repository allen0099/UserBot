import json
import logging
import os

log: logging.Logger = logging.getLogger(__name__)
FILE_PATH = os.getcwd() + "/auth_user.json"


def add_auth(uid: int) -> None:
    with open(FILE_PATH, "r") as f:
        s: str = f.read()
    file: dict = json.loads(s)
    users: list = file['auth']

    if uid not in users:
        users.append(uid)
        file['auth'] = users

    string: str = json.dumps(file)

    with open(FILE_PATH, "w") as f:
        f.write(string)


def remove_auth(uid: int) -> None:
    with open(FILE_PATH, "r") as f:
        s: str = f.read()
    file: dict = json.loads(s)
    users: list = file['auth']

    if uid in users:
        users.remove(uid)
        file['auth'] = users

    string: str = json.dumps(file)

    with open(FILE_PATH, "w") as f:
        f.write(string)


def get_auth() -> list:
    with open(FILE_PATH, "r") as f:
        s: str = f.read()
    file: dict = json.loads(s)
    users: list = file['auth']
    return users
