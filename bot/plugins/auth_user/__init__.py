# 該 package 可以新增、刪除、列出在資料庫裡面的使用者 UID
# 只有 me 允許操作
import logging
import re
from typing import Pattern

log: logging.Logger = logging.getLogger(__name__)

USERNAME_RE: Pattern[str] = re.compile(r"(?<=t\.me/)\w{5,}$|(?<=@)\w{5,}$|\w{5,}$|^[+-]?\d+$|me$|self$")
