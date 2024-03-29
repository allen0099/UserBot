import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.sql.functions import now

from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)


class FullNameBlacklist(db.BASE):
    __tablename__: str = "blacklist_fullname"

    word: str = Column(String, nullable=False, primary_key=True)
    """名字中不能包含的字詞"""

    count: int = Column(Integer, nullable=False, default=0)
    """被檢查到的次數"""
    disabled: bool = Column(Boolean, nullable=False, default=False)
    """規則是否停用"""
    created_by: int = Column(BigInteger, nullable=False)
    """建立規則的使用者"""
    created_at: datetime = Column(
        DateTime, nullable=False, default=func.now(), server_default=now()
    )
    """建立規則的時間"""

    @staticmethod
    def get(word: str) -> Optional["FullNameBlacklist"]:
        return db.session.query(FullNameBlacklist).filter_by(word=word).first()

    @staticmethod
    def create(word: str, count: int, created_by: int) -> None:
        if FullNameBlacklist.get(word):
            return

        f = FullNameBlacklist()

        f.word = word
        f.count = count
        f.created_by = created_by
        db.session.add(f)
        db.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.commit()
