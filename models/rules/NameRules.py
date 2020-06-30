from typing import List

from sqlalchemy import *

from models import Base, session


class NameRules(Base):
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
        _check: NameRules = session.query(NameRules).filter_by(rule=rule).first()
        if _check is None:
            session.add(NameRules(rule))
            session.commit()
            return True
        return False

    @staticmethod
    def remove(_id: str) -> bool:
        _check: NameRules = session.query(NameRules).filter_by(id=_id).first()
        if _check is not None:
            session.delete(_check)
            session.commit()
            return True
        return False

    @staticmethod
    def get_all() -> List["NameRules"]:
        return session.query(NameRules).all()

    @staticmethod
    def find_by_id(_id: int) -> "NameRules":
        return session.query(NameRules).filter_by(id=_id).first()

    @staticmethod
    def edit(_id: int, new_rule: str) -> bool:
        _check: NameRules = session.query(NameRules).filter_by(id=_id).first()
        if _check is not None:
            _check.rule = new_rule
            session.commit()
            return True
        return False

    @staticmethod
    def is_exist(_id: int) -> bool:
        rule: NameRules = session.query(NameRules).filter_by(id=_id).first()
        if rule is None:
            return False
        return True
