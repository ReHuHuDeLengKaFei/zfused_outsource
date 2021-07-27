# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import time
import logging
import datetime

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


class Prophet(_Entity):
    global_dict = {}
    global_tags = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(Prophet, self).__init__("prophet", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("prophet", self._id)
                if not _data:
                    logger.error("prophet id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def unprophet(self):
        if self.global_dict[self._id]["Value"] == 1:
            return True
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _user_id = zfused_api.zFused.USER_ID
        self.global_dict[self._id]["Value"] = 1
        self._data["Value"] = 1
        self.global_dict[self._id]["SolverId"] = _user_id
        self._data["SolverId"] = _user_id
        self.global_dict[self._id]["SolvedTime"] = _current_time
        self._data["SolvedTime"] = _current_time
        v = self.put("prophet", self._data["Id"], self._data, "value")
        if v:
            return True
        else:
            return False