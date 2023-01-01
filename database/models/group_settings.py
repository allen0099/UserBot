import logging
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime
from sqlalchemy.sql.functions import now

from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)


class GroupSettings(db.BASE):
    __tablename__ = "group_settings"

    id: int = Column(BigInteger, autoincrement=True, primary_key=True)
    group_id: int = Column(BigInteger, nullable=False)

    new_member_detect: bool = Column(Boolean, nullable=False, default=True)
    """檢查新入群成員姓名、簡介、第三方 API (Combot)"""

    new_message_check: bool = Column(Boolean, nullable=False, default=True)
    """檢查使用者新入群的前幾條訊息是否符合驗證規則"""

    created_at: datetime = Column(
        DateTime, nullable=False, default=datetime.now(), server_default=now()
    )
    update_at: datetime = Column(
        DateTime,
        nullable=False,
        default=datetime.now(),
        server_default=now(),
        onupdate=datetime.now(),
    )
