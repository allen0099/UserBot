# 授權使用者的增加、刪除、列出，只有 me 能用
import logging
import re
from typing import Pattern

log: logging.Logger = logging.getLogger(__name__)

USERNAME_RE: Pattern[str] = re.compile(r"(?<=t\.me/)\w{5,}$|(?<=@)\w{5,}$|\w{5,}$|^[+-]?\d+$|me$|self$")
