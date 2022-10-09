import logging

from sqlalchemy import BigInteger, Column, Enum

from bot.enums import PermissionLevel
from core.log import main_logger
from database import db

log: logging.Logger = main_logger(__name__)


class User(db.BASE):
    """任何可以發言的對象，包括群組、頻道、個人"""

    __tablename__: str = "users"

    id: int = Column(BigInteger, primary_key=True)
    level: PermissionLevel = Column(
        Enum(PermissionLevel), nullable=False, default=PermissionLevel.OTHER
    )
