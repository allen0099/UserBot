import logging
import re
from typing import List

log: logging.Logger = logging.getLogger(__name__)


def check_rules(target: str, rules: List[str]) -> str:
    for rule in rules:
        result: re.Match = re.search(rule, target)

        log.debug(f"Checking rule: {rule}")

        if result is not None:
            match = result.group()
            return f"<code>===MATCH===</code>\n" \
                   f"Rule: <code>{rule}</code>\n" \
                   f"Match: <code>{match}</code>\n"
