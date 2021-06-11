import logging

from .admin_required import _admin_required

log: logging.Logger = logging.getLogger(__name__)


class CustomFilters:
    admin_required = _admin_required
