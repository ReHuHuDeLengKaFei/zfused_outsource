# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


class Entity(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Entity, self).__init__("entity", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("entity", self._id)
                if not _data:
                    logger.error("entity id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]


class ProjectEntity(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ProjectEntity, self).__init__("project_entity", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("project_entity", self._id)
                if not _data:
                    logger.error("project entity id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    # def file_path(self):
    #     return self.code()

    # def color(self):
    #     """ return step color
    #         step数据库需要增加color属性,调用project step color效率低
    #     """
    #     _color = self._data["Color"]
    #     if _color:
    #         return _color
    #     # get project step color
    #     _step_handle = Step(self._data["StepId"])
    #     return _step_handle.color()

    def sort(self):
        return self._data["Sort"]

    def path(self):
        _path = self.code()

        _custom_path = self._data.get("CustomPath")
        if _custom_path:
            _path = self.get_custom_path(_custom_path)
        return _path

    def update_custom_path(self, custom_path):
        if self.global_dict[self._id]["CustomPath"] == custom_path:
            return True
        self.global_dict[self._id]["CustomPath"] = custom_path
        self._data["CustomPath"] = custom_path
        v = self.put("project_entity", self._data["Id"], self._data, "custom_path")
        if v:
            return True
        else:
            return False