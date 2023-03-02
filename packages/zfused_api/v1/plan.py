# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import os
import time
import datetime
import shutil
import logging
import re

from . import _Entity
import zfused_api


logger = logging.getLogger(__name__)


def cache(project_id_list = []):
    """ init project assets
    """

    _s_t = time.time()
    # if extract_freeze:
    #     _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    # else:
    #     _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    # _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])

    if not project_id_list:
        _plans = zfused_api.zFused.get("plan")
    else:
        _project_ids = "|".join(map(str,project_id_list))
        _plans = zfused_api.zFused.get("plan", filter = {"ProjectId__in": _project_ids})
    if _plans:
        list(map(lambda _plan: Plan.global_dict.setdefault(_plan["Id"],_plan), _plans))
    _e_t = time.time()
    logger.info("plan cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _plans


class Plan(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Plan, self).__init__("plan", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("plan", self._id)
                if not isinstance(_data, dict):
                    logger.error("plan id {0} not exists".format(self._id))
                    self._data = {}
                    return None
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def full_name_code(self):
        return zfused_api.objects.Objects(self._data.get("EntityType"),self._data.get("EntityId")).full_name_code()

    def project(self):
        _project_id = self._data.get("ProjectId")
        if _project_id:
            return zfused_api.project.Project(_project_id)
        return None

    def entity(self):
        return zfused_api.objects.Objects(self._data.get("EntityType"), self._data.get("EntityId"))

    def entity_type(self):
        _entity_type = self._data.get("EntityType")
        if _entity_type:
            return _entity_type
        return None

    def color(self):
        _color = self._data.get("Color")
        if not _color:
            if self.entity_type() == "project_step":
                _color = self.entity().color()
        return _color if _color else "#217346"

    def start_time(self):
        """ get start time
        rtype: datetime.datetime
        """
        _time_text = self._data["StartTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def end_time(self):
        """ get end time
        rtype: datetime.datetime
        """
        _time_text = self._data["EndTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def update_start_time(self, time_str):
        """ update start time
        """  
        if self._data["StartTime"].split("+")[0] == time_str.split("+")[0]:
            return False
        self.global_dict[self._id]["StartTime"] = time_str
        self._data["StartTime"] = time_str
        v = self.put("plan", self._data["Id"], self._data, "start_time")
        if v:
            return True
        else:
            return False

    def update_end_time(self, time_str):
        """ update end time
        """ 
        if self._data["EndTime"].split("+")[0] == time_str.split("+")[0]:
            return False
        self.global_dict[self._id]["EndTime"] = time_str
        self._data["EndTime"] = time_str
        v = self.put("plan", self._data["Id"], self._data, "end_time")
        if v:
            return True
        else:
            return False