# coding:utf-8
# --author-- lanhua.zhou

""" 职位操作api
"""
from __future__ import print_function

from collections import defaultdict
from collections import OrderedDict

import os
import time
import shutil
import datetime
import logging
import copy

from . import _Entity
import zfused_api

from . import worktime

logger = logging.getLogger(__name__)


def clear(lis):
    del lis[:]

def cache(project_ids = [], extract_freeze = True):
    """ get project developments 
        init 
    """
    _s_t = time.clock()
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])
    if not project_ids:
        _developments = zfused_api.zFused.get("development", filter = {"StatusId__in": _status_ids} )
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_ids])
        _developments = zfused_api.zFused.get("development", filter = {"ProjectId__in": _project_ids, "StatusId__in": _status_ids})
    if _developments:
        list(map(lambda _development: Development.global_dict.setdefault(_development["Id"],_development), _developments))
    _e_t = time.clock()
    logger.info("development cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _developments

def cache_from_ids(ids, extract_freeze = True):
    _s_t = time.clock()
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])
    ids = "|".join(map(str, ids))
    _developments = zfused_api.zFused.get("development", filter = {"Id__in": ids, "StatusId__in": _status_ids})
    if _developments:
        list(map(lambda _development: Development.global_dict.setdefault(_development["Id"],_development), _developments))
    _e_t = time.clock()
    logger.info("development cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _developments



class Development(_Entity):


    @classmethod
    def new(cls, project_id, project_step_id, title, user_ids, thumbnail_path, description = ""):
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        # _task = zfused_api.task.Task(task_id)
        _status_id = zfused_api.status.active_status_ids()[0]

        _development, _status = zfused_api.zFused.post( key = "development", 
                                                        data = { "ProjectId": project_id,
                                                                 "ProjectStepId": project_step_id,
                                                                 "Name": title,
                                                                 "Description": description,
                                                                 "ThumbnailPath": thumbnail_path,
                                                                 "StatusId": _status_id,
                                                                 "Active": "true",
                                                                 "CreatedBy": _created_by,
                                                                 "CreatedTime": _created_time } )
        if not _status:
            return u"{} create error".format(title), False

        _development_id = _development.get("Id")

        # group user
        for _user_id in user_ids:
            zfused_api.zFused.post( "group_user", { "EntityType": "development", 
                                        "EntityId": _development_id, 
                                        "UserId": _user_id,
                                        "CreatedBy": _created_by,
                                        "CreatedTime": _created_time })

        zfused_api.im.submit_message( "user",
                                      _created_by,
                                      user_ids,
                                      {"entity_type": "development",
                                       "entity_id": _development_id},
                                      "development", 
                                      "development",
                                      _development_id,
                                      "development",
                                      _development_id )

        return _development_id, True


    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Development, self).__init__("development", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("development", self._id)
                if not _data:
                    logger.error("development id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def object(self):
        return "development"

    def title(self):
        return self.name()

    def name_code(self):
        return self.name()

    @_Entity._recheck
    def project_id(self):
        return self._data.get("ProjectId")    

    def project(self):
        return zfused_api.project.Project(self._data.get("ProjectId"))
    
    def project_step(self):
        _project_step_id = self._data.get("ProjectStepId")
        if _project_step_id:
            return zfused_api.step.ProjectStep(_project_step_id)
        return None

    def project_step_id(self):
        return self.global_dict[self._id]["ProjectStepId"]

    def status(self):
        return zfused_api.status.Status(self._data.get("StatusId"))

    def status_id(self):
        return self._data.get("StatusId")

    def update_status(self, status_id):
        """ update status
        :param status_id: 状态id
        :rtype: bool
        """
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

        if self.status_id() == status_id:
            return 

        self.global_dict[self._id]["StatusId"] = status_id
        self._data["StatusId"] = status_id
        v = self.put("development", self._data["Id"], self._data, "status_id")
        if v:
            return True
        else:
            return False

    def user_id(self):
        return self._data.get("AssignedTo")

    def update_assigned(self, user_id):
        """
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["AssignedTo"] == user_id:
            return True

        self.global_dict[self._id]["AssignedTo"] = user_id
        self._data["AssignedTo"] = user_id
        v = self.put("development", self._data["Id"], self._data, "assigned_to")
        if v:
            return True
        else:
            return False

    def start_time(self):
        """get start time
        rtype: datetime.datetime
        """
        _time_text = self._data["StartTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def update_start_time(self, time_str):
        """ update start time
        """  
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self._data["StartTime"].split("+")[0] == time_str.split("+")[0]:
            return False

        self.global_dict[self._id]["StartTime"] = time_str
        self._data["StartTime"] = time_str
        v = self.put("development", self._id, self._data, "start_time")
        if v:
            return True
        else:
            return False

    def end_time(self):
        """ 
        get end time
        rtype: datetime.datetime
        """
        _time_text = self._data["DueTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def update_end_time(self, time_str):
        """ update end time
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self._data["DueTime"].split("+")[0] == time_str.split("+")[0]:
            return False

        self.global_dict[self._id]["DueTime"] = time_str
        self._data["DueTime"] = time_str
        v = self.put("development", self._id, self._data, "due_time")
        if v:
            return True
        else:
            return False

    def update_estimated_time(self, hour):
        """ update estimated time
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self._data["EstimatedTime"] == hour:
            return False
            
        self._data["EstimatedTime"] = hour
        self.global_dict[self._id]["EstimatedTime"] = hour
        v = self.put("development", self._data["Id"], self._data, "estimated_time")
        if v:
            return True
        else:
            return False
    
    def description(self):
        return self._data.get("Description")

    def update_description(self, _description):
        self.global_dict[self._id]["Description"] = _description
        self._data["Description"] = _description
        v = self.put("development", self._data["Id"], self._data, "description")
        if v:
            return True
        else:
            return False

    def level(self):
        """ get asset level
        """
        return self._data["Level"]

    def update_level(self, index):
        """
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["Level"] == index:
            return True

        self.global_dict[self._id]["Level"] = index
        self._data["Level"] = index
        v = self.put("development", self._data["Id"], self._data, "level")
        if v:
            return True
        else:
            return False

    def priority(self):
        return self._data["Priority"]

    def update_priority(self, priority_index):
        """
        """ 
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data
        if self.global_dict[self._id]["Priority"] == priority_index:
            return True

        self.global_dict[self._id]["Priority"] = priority_index
        self._data["Priority"] = priority_index
        v = self.put("development", self._data["Id"], self._data, "priority")
        if v:
            return True
        else:
            return False

    def thumbnail(self):
        """ get thumbnai name
        """
        return self.global_dict[self._id]["Thumbnail"]

    def get_thumbnail(self, is_version = False):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None