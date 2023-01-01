import logging
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql.functions import now

from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)


class WordBlacklist(db.BASE):
    __tablename__: str = "blacklist_word"

    word: str = Column(String, nullable=False, primary_key=True)
    """字串中不能包含的字詞"""
    check_edit: bool = Column(Boolean, nullable=False, default=True)
    """檢查編輯後的訊息"""

    count: int = Column(Integer, nullable=False, default=0)
    """被檢查到的次數"""
    disabled: bool = Column(Boolean, nullable=False, default=False)
    """規則是否停用"""
    created_by: int = Column(BigInteger, nullable=False)
    """建立規則的使用者"""
    created_at: datetime = Column(
        DateTime, nullable=False, default=datetime.now(), server_default=now()
    )
    """建立規則的時間"""
