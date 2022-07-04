# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import time
import logging
import datetime

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


class ProductionFile(_Entity):
    global_dict = {}
    global_tags = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(ProductionFile, self).__init__("production_file", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("production_file", self._id)
                if not _data:
                    logger.error("production_file id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def path(self):
        return self._data.get("Path")

    def suffix(self):
        return self._data.get("Suffix")

    def format(self):
        return self._data.get("Format")

    def task(self):
        return zfused_api.task.Task( self._data.get("TaskId") )

    def task_id(self):
        return self._data.get("TaskId")

    def project_entity_type(self):
        return self._data.get("ProjectEntityType")

    def project_entity_id(self):
        return self._data.get("ProjectEntityId")

    def project_entity(self):
        if self._data.get("RelativeEntityId"):
            return zfused_api.objects.Objects(self._data["RelativeEntityType"], self._data["RelativeEntityId"])
        return zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"])

    def get_thumbnail(self):
        return self.project_entity().get_thumbnail()

    def size(self):
        return self._data.get("Size")

    def attr_output_id(self):
        return self._data.get("ProjectStepAttrId")

    def attr_output(self):
        return zfused_api.attr.Output(self._data.get("ProjectStepAttrId"))