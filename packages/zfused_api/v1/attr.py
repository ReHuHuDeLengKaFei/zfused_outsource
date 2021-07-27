# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import logging
import datetime

from . import _Entity
import zfused_api


logger = logging.getLogger(__name__)


class Input(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Input, self).__init__("attr_input", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("attr_input", self._id)
                if not _data:
                    logger.error("attr_input id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def project_step_id(self):
        return self._data.get("ProjectStepId")

    def project_step(self):
        return zfused_api.step.ProjectStep(self._data.get("ProjectStepId"))

    def format(self):
        return self._data.get("Format")
    
    def suffix(self):
        return self._data.get("Suffix")

    def script(self):
        return self._data.get("Script")

    def extended_version(self):
        return self._data.get("ExtendedVersion")


class Output(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Output, self).__init__("attr_output", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("attr_output", self._id)
                if not _data:
                    logger.error("attr_output id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def project_step_id(self):
        return self._data.get("ProjectStepId")

    def project_step(self):
        return zfused_api.step.ProjectStep(self._data.get("ProjectStepId"))

    def format(self):
        return self._data.get("Format")
    
    def suffix(self):
        return self._data.get("Suffix")

    def script(self):
        return self._data.get("Script")



# class TaskAttr():
#     def __init__(self, task_id, attr_id = 0, mode = "in"):
#         if mode == "in":
#             self._attr = Input(attr_id)
#         elif mode == "out":
#             self._attr = Output(attr_id)
#         self._mode = mode
#         self._task = zfused_api.task.Task(task_id)
    
#     def mode(self):
#         return self._mode