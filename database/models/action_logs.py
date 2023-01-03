import logging
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, func
from sqlalchemy.sql.functions import now

from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)


class ActionLogs(db.BASE):
    """紀錄被自動封鎖的原因跟其他資訊"""

    __tablename__ = "action_logs"

    id: int = Column(BigInteger, autoincrement=True, primary_key=True)
    group_id: int = Column(BigInteger, nullable=False)

    target_id: int = Column(BigInteger, nullable=False)
    """被封鎖的 ID"""
    reason: str = Column(String, nullable=False)
    """封鎖原因"""
    source: str = Column(String, nullable=False)
    """封鎖來源 (其他黑名單來源)"""
    message: str = Column(String, nullable=False)
    """原始訊息內容 repr"""
    viewable: bool = Column(Boolean, nullable=False, default=True)
    """管理員是否允許調閱封鎖原因及原始訊息內容"""

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
