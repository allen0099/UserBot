import logging
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, func
from sqlalchemy.sql.functions import now

from bot.enums import PermissionLevel
from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)


class Users(db.BASE):
    """任何可以發言的對象，包括群組、頻道、個人"""

    __tablename__: str = "users"

    id: int = Column(BigInteger, primary_key=True)
    """使用者 ID"""
    level: PermissionLevel = Column(
        Enum(PermissionLevel), nullable=False, default=PermissionLevel.OTHER
    )
    """使用者等級，預設是其他"""
    locked: bool = Column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    """如果使用者被鎖定，只有擁有者可以修改權限等級"""

    created_at: datetime = Column(
        DateTime, nullable=False, default=func.now(), server_default=now()
    )
    update_at: datetime = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=now(),
        onupdate=func.now(),
    )

    def __init__(self, id: int, level: PermissionLevel = PermissionLevel.OTHER) -> None:
        self.id = id
        self.level = level

    @staticmethod
    def get(_id: int) -> "Users":
        """取得使用者"""
        user: Users = db.session.query(Users).filter_by(id=_id).first()

        if user:
            return user

        return Users(_id)

    def add(self) -> None:
        """新增使用者到資料庫"""
        db.session.add(self)
        db.commit()
