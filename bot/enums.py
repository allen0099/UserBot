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


class EmojiList(str, Enum):
    EMPTY = ""
    TRUE = "✅"
    FALSE = "❎"

    DENY = "😢"
    INFO = "ℹ"
    DELETE = "🗑️"
    BAN = "🚫"
    ADD_MEMBER = "🔗"
    PIN = "📌"
    VOICE = "🔊"
    ADD_ADMIN = "➕"

    BOT = "🤖"
    BOT_EYES = "👀"
    BOT_CLOSE_EYES = "🕶"
