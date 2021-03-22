from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from database.mixin import BaseMixin
from main import db


class Name(db.base, BaseMixin):
    category: str = Column(String(20), nullable=False)
    match: str = Column(String(100), nullable=False)

    PREFIX: str = "PREFIX"
    CONTAIN: str = "CONTAIN"

    def __init__(self, category: str):
        self.category = category

    @staticmethod
    def get_dict(category: str):
        session: Session = db.get_session()
        s = session.query(Name).filter_by(category=category).all()
        return s
