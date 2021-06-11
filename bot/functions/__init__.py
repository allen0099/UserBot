import logging

from .delete_range_messages import DeleteRangeMessages
from .get_members import GetMembers

log: logging.Logger = logging.getLogger(__name__)


class CustomFunctions(
    DeleteRangeMessages,
    GetMembers
):
    pass
