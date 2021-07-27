# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import shutil
import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


class Participant(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Participant, self).__init__("review", entity_id, entity_data)

# class Participant(zfused_api.zFused):
#     def __init__(self, id, data = None):
#         self._id = id
#         self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("review", self._id)
                if not _data:
                    logger.error("review id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    # def object(self):
    #     return "participant"

    # def id(self):
    #     return self._id
