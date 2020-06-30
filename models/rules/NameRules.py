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
    def remove(id: str) -> bool:
        _check: NameRules = session.query(NameRules).filter_by(id=id).first()
        if _check is not None:
            session.delete(_check)
            session.commit()
            return True
        return False

    @staticmethod
    def get_id(rule: str) -> int:
        _check: NameRules = session.query(NameRules).filter_by(rule=rule).first()
        return _check.id

    @staticmethod
    def get_rules() -> List[str]:
        _rules: List[NameRules] = session.query(NameRules).all()
        return [r.rule for r in _rules]
