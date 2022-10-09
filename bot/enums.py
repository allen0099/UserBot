from enum import Enum, auto


class PermissionLevel(Enum):
    OWNER = auto()
    EXECUTOR = auto()
    WHITE = auto()
    BLACK = auto()
    OTHER = auto()


class ActionsList(Enum):
    DELETE_ALL = auto()
    DELETE_ONE = auto()
    DELETE_ALL_AND_BAN = auto()
    DO_NOTHING = auto()
