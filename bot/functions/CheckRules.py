import logging
import re
from typing import List

log: logging.Logger = logging.getLogger(__name__)


class CheckRules(object):

    def __init__(self, target: str, rules: List[str]) -> None:
        for rule in rules:
            result: re.Match = re.search(rule, target)

            log.debug(f"Checking rule: {rule}")

            if result is not None:
                self.times = len(re.findall(rule, target))
                self.rule = rule
                self.match = result.group()
                break

    def __str__(self) -> str:
        return f"<code>===MATCH===</code>\n" \
               f"Rule: <code>{self.rule}</code>\n" \
               f"Match: <code>{self.match}</code>\n"

    def __bool__(self) -> bool:
        return True if hasattr(self, "match") else False

    def __add__(self, other) -> str:
        if isinstance(other, str):
            return self.__str__() + other

    def __radd__(self, other) -> str:
        if isinstance(other, str):
            return other + self.__str__()
