# 授權使用者的增加、刪除、列出，只有 me 能用
import logging
import re
from typing import Pattern

log: logging.Logger = logging.getLogger(__name__)

# Find all characters after command
CMD_RE: Pattern[str] = re.compile(r"(?s)(?<=\w ).+")
# Find username, uid, phone in command
USERNAME_RE: Pattern[str] = re.compile(r"(?<=t\.me/)\w{5,}$|(?<=@)\w{5,}$|\w{5,}$|^[+-]?\d+$|me$|self$")
