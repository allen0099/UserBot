import datetime
import logging

from sqlalchemy import Column, TIMESTAMP, text
from sqlalchemy.ext.declarative import declared_attr

log: logging.Logger = logging.getLogger(__name__)


class TimestampMixin(object):
    @declared_attr
    def updated_at(self):
        return Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    @declared_attr
    def expired_at(self):
        return Column(TIMESTAMP, default=datetime.datetime.utcnow() + datetime.timedelta(hours=6))
