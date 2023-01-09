import logging
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, func
from sqlalchemy.sql.functions import now

from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)

GBAN_STR: str = "Global banned"


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

    def __init__(
        self, target_id: int, group_id: int, reason: str, source: str, message: str
    ) -> None:
        self.target_id = target_id
        self.group_id = group_id
        self.reason = reason
        self.source = source
        self.message = message

    @staticmethod
    def create(
        target_id: int, group_id: int, reason: str, source: str, message: str
    ) -> None:
        _data: ActionLogs = ActionLogs(target_id, group_id, reason, source, message)
        db.session.add(_data)
        db.commit()

    @staticmethod
    def create_user_gban_log(target_id: int, group_id: int, executor_id: int) -> None:
        ActionLogs.create(
            target_id, group_id, GBAN_STR, f"{executor_id}", "Manually banned"
        )

    @staticmethod
    def create_chat_gban_log(target_id: int, executor_id: int) -> None:
        ActionLogs.create(target_id, 0, GBAN_STR, f"{executor_id}", "Manually banned")

    @staticmethod
    def get_banned_logs(target_id: int) -> list["ActionLogs"]:
        return db.session.query(ActionLogs).filter_by(target_id=target_id).all()

    @staticmethod
    def destroy_all_logs(target_id: int) -> None:
        db.session.query(ActionLogs).filter_by(target_id=target_id).delete()
        db.commit()
