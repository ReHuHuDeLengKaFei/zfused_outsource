# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


class ProjectComponent(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ProjectComponent, self).__init__("project_component", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("project_component", self._id)
                if not _data:
                    logger.error("project component id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]