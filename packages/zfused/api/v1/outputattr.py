# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


class OutputAttr(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(OutputAttr, self).__init__("step_attr_output", entity_id, entity_data)
        
        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("step_attr_output", self._id)
                if not _data:
                    logger.error("step_attr_output id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def script(self):
        """
        get script

        rtype: str
        """
        return u"{}".format(self._data["Script"])

    def suffix(self):
        return self._data["Suffix"]

    def format(self):
        return self._data["Format"]

    def path(self):
        return self._data.get("Code")