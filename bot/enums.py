from enum import Enum, auto


class LogTopics(int, Enum):
    """回復訊息主題的 message ID，會因為紀錄頻道而改變"""

    default: int = 1
    new_user: int = 2
    global_ban: int = 6
    auto: int = 14
    action: int = 16
    banned: int = 24
    debug: int = 751

    error: int = 512


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
    change_info = "ℹ"
    post_messages = "📝"
    edit_messages = "✏"
    delete_messages = "🗑️"
    ban_users = "🚫"
    invite_users = "🔗"
    pin_messages = "📌"
    add_admins = "➕"
    anonymous = "👤"
    manage_call = "🔊"
    other = "🔧"

    BOT = "🤖"
    BOT_EYES = "👀"
    BOT_CLOSE_EYES = "🕶"
