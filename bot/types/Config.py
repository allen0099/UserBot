import logging
from dataclasses import dataclass

log: logging.Logger = logging.getLogger(__name__)


@dataclass
class Config:
    log_channel: str
