import logging

from sqlalchemy import BigInteger, Column, String

from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)


class Record(db.BASE):
    """觸發紀錄"""

    __tablename__: str = "records"

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)
    """紀錄編號"""
    triggered_by: int = Column(BigInteger, nullable=False)
    """觸發者"""
    triggered_at: int = Column(BigInteger, nullable=False)
    """觸發地點"""
    triggered_function: str = Column(String, nullable=False, default="unknown")
    """觸發功能"""
    message: str = Column(String, nullable=False)
    """觸發訊息"""

    def __init__(
        self,
        triggered_by: int,
        triggered_at: int,
        triggered_function: str,
        message: str,
    ):
        self.triggered_by = triggered_by
        self.triggered_at = triggered_at
        self.triggered_function = triggered_function
        self.message = message

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
