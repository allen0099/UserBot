from typing import List

from sqlalchemy import *

from models import Base, session


class Name(Base):
    __tablename__: str = "name"

    id: int = Column(
        Integer,
        primary_key=True
    )
    rule: str = Column(
        String
    )

    def __init__(self, rule: str) -> None:
        self.rule = rule

    def __repr__(self) -> str:
        return f"Name {self.id}"

    @staticmethod
    def add(rule: str) -> bool:
        _check: Name = session.query(Name).filter_by(rule=rule).first()
        if _check is None:
            session.add(Name(rule))
            session.commit()
            return True
        return False

    @staticmethod
    def remove(rule: str) -> bool:
        _check: Name = session.query(Name).filter_by(rule=rule).first()
        if _check is not None:
            session.delete(_check)
            session.commit()
            return True
        return False

    @staticmethod
    def get() -> List[str]:
        _rules: List[Name] = session.query(Name).all()
        return [r.rule for r in _rules]
