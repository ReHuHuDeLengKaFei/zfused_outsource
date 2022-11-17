# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)

__all__ = ["Approval"]


class Approval(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Approval, self).__init__("approval", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("approval", self._id)
                if not _data:
                    logger.error("approval id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data

        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]
                
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

    def status(self):
        return self._data.get("Status")

    def full_name_code(self):
        return zfused_api.objects.Objects(self._data["Object"], self._data["ObjectId"]).full_name_code()

    @_Entity._recheck
    def submit(self, _s, _des = None):
        currentTime = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        self.global_dict[self._id]["ApprovalId"] = self.USER_ID
        self.global_dict[self._id]["ApprovalTime"] = currentTime
        self.global_dict[self._id]["Status"] = _s
        self.global_dict[self._id]["Descriptyion"] = _des

        self._data["ApprovalId"] = self.USER_ID
        self._data["ApprovalTime"] = currentTime
        self._data["Status"] = _s
        self._data["Descriptyion"] = _des
        v = self.put("approval", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    @_Entity._recheck
    def is_approval(self):
        return self.global_dict[self._id]["Status"]

    @_Entity._recheck
    def update_approval(self, is_approval):
        if self._data.get("Status") == is_approval:
            return 

        self.global_dict[self._id]["Status"] = is_approval
        self._data["Status"] = is_approval
        v = self.put("approval", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False
    @_Entity._recheck
    def task(self):
        return zfused_api.task.Task(self._data.get("TaskId"))

    @_Entity._recheck
    def task_id(self):
        return self._data.get("TaskId")


class ApprovalProcess(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ApprovalProcess, self).__init__("review_process", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("review_process", self._id)
                if not _data:
                    logger.error("review process id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]