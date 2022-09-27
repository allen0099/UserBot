from enum import Enum, auto


class PermissionLevel(Enum):
    BOT_OWNER = auto()
    EXECUTOR = auto()
    WHITE_USER = auto()
    BLACK_USER = auto()
    OTHER = auto()


class ActionsList(Enum):
    DELETE_ALL = auto()
    DELETE_ONE = auto()
    DELETE_ALL_AND_BAN = auto()
    DO_NOTHING = auto()
