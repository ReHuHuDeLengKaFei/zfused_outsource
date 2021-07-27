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


def new(task_id, title, thumbnail, description, introduction, relatives = []):
    # created by and user
    _created_time = "{}+00:00".format( datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") )
    _created_by = zfused_api.zFused.USER_ID
    
    _task_handle = zfused_api.task.Task(task_id)
    _project_id = _task_handle.project_id()
    _project_step_id = _task_handle.project_step_id()
    _project_entity_type = _task_handle.project_entity_type()
    _project_entity_id = _task_handle.project_entity_id()

    _value, _status = zfused_api.zFused.post(key = "feedback", data = { "ProjectId": _project_id,
                                                                        "ProjectStepId": _project_step_id,
                                                                        "ProjectEntityType": _project_entity_type,
                                                                        "ProjectEntityId": _project_entity_id,
                                                                        "TaskId": task_id,
                                                                        "Title": title,
                                                                        "ThumbnailPath": thumbnail,
                                                                        "Description": description,
                                                                        "Introduction": str(introduction),
                                                                        "Value": 0,
                                                                        "Relatives": str(relatives),
                                                                        "CreatedBy": _created_by,
                                                                        "CreatedTime": _created_time })
    if _status:
        if relatives:
            for _relative in relatives:
                zfused_api.zFused.post( key = "feedback_relative", data = { "FeedbackId": _value.get("Id"),
                                                                            "ProjectId": _relative.get("project_id"),
                                                                            "ProjectStepId": _relative.get("project_step_id"),
                                                                            "ProjectEntityType": _relative.get("project_entity_type"),
                                                                            "ProjectEntityId": _relative.get("project_entity_id"),
                                                                            "TaskId": _relative.get("task_id"),
                                                                            "IsRelative": int(_relative.get("is_relative")),
                                                                            "Value": int(_relative.get("value")),
                                                                            "CreatedBy": _created_by,
                                                                            "CreatedTime": _created_time } )

        return FeedBack(_value["Id"], _value), True

    return "create error", False


def cache(project_id = []):
    """ init project versions
    """
    FeedBack.global_dict = {}
    if not project_id:
        _feedbacks = zfused_api.zFused.get("feedback", sortby = ["Id"], order = ["desc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _feedbacks = zfused_api.zFused.get("feedback", filter = {"ProjectId__in": _project_ids}, sortby = ["Id"], order = ["desc"])
    if _feedbacks:
        list(map(lambda _feedback: FeedBack.global_dict.setdefault(_feedback["Id"],_feedback), _feedbacks))
    return _feedbacks

def cache_from_ids(ids):
    ids = "|".join(map(str, ids))
    _feedbacks = zfused_api.zFused.get("feedback", filter = {"Id__in": ids})
    if _feedbacks:
        list(map(lambda _feedback: FeedBack.global_dict.setdefault(_feedback["Id"],_feedback), _feedbacks))
    return _feedbacks


class FeedBack(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(FeedBack, self).__init__("feedback", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("feedback", self._id)
                if not isinstance(_data, dict):
                    logger.error("feedback id {0} not exists".format(self._id))
                    self._data = {}
                    return None
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]
                
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data

    def title(self):
        return self._data.get("Title")

    def name(self):
        return self._data.get("Title")

    def full_name_code(self):
        return self._data.get("Title")

    def get_thumbnail(self, is_version = False):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

    def project(self):
        return zfused_api.project.Project(self._data.get("ProjectId"))

    def project_entity_type(self):
        return self._data["ProjectEntityType"]

    def project_entity_id(self):
        return self._data["ProjectEntityId"]

    def project_entity(self):
        return zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"])

    def project_step_id(self):
        return self._data.get("ProjectStepId")

    def project_step(self):
        return zfused_api.step.ProjectStep(self._data.get("ProjectStepId"))

    def status(self):
        return self._data.get("Value")
    
    def description(self):
        return self._data.get("Description")

    def relatives(self):
        return self._data.get("Relatives")
    
    def resubmit_relatives(self, relatives):
        _relatives = str(relatives)
        self.global_dict[self._id]["Relatives"] = _relatives
        self._data["Relatives"] = _relatives
        v = self.put("feedback", self._data["Id"], self._data, "relatives")
        if v:
            return True
        else:
            return False

    def update_relatives(self, project_step_id, relative):
        _relatives = self.relatives()
        _relatives = eval(_relatives)
        for _index, _relative in enumerate(_relatives):
            _project_step_id = _relative.get("project_step_id")
            if project_step_id == _project_step_id:
                for _key, _value in relative.items():
                    _relative[_key] = _value
                    if _key == "is_relative" or _key == "value":
                        _key_field = "".join( [_field.capitalize() for _field in _key.split("_")] )
                        _feedback_relative = zfused_api.zFused.get("feedback_relative", filter = { "FeedbackId": self._id,
                                                                                                   "ProjectStepId": _project_step_id })
                        if _feedback_relative:
                            _feedback_relative = _feedback_relative[0]
                            _feedback_relative[_key_field] = int(_value)
                            self.put("feedback_relative", _feedback_relative["Id"], _feedback_relative, _key, False)
                break
        _relatives = str(_relatives)
        self.global_dict[self._id]["Relatives"] = _relatives
        self._data["Relatives"] = _relatives
        v = self.put("feedback", self._data["Id"], self._data, "relatives")
        if v:
            return True
        else:
            return False

    def update_solve(self, value):
        if self._data.get("Value") == value:
            return 
        self.global_dict[self._id]["Value"] = value
        self._data["Value"] = value
        v = self.put("feedback", self._data["Id"], self._data, "value")
        if v:
            return True
        else:
            return False

    def user_ids(self):
        # 消息组成员
        _user_ids = [zfused_api.zFused.USER_ID]
        _project_step = self.project_step()
        _user_ids += _project_step.cc_user_ids() + _project_step.approvalto_user_ids() +  _project_step.review_user_ids()

        _relatives = self.relatives()
        _relatives = eval(_relatives)
        if _relatives:
            for _relative in _relatives:
                if _relative.get("is_relative"):
                    _relative_project_step = zfused_api.step.ProjectStep(_relative.get("project_step_id"))
                    _relative_task = zfused_api.task.Task(_relative.get("task_id"))
                    _user_ids += [_relative_task.assigned_to()]
                    _user_ids += _relative_project_step.review_user_ids() + _relative_project_step.cc_user_ids() + _relative_project_step.approvalto_user_ids() 

        return _user_ids

class FeedBackRelative(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(FeedBackRelative, self).__init__("feedback", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("feedback", self._id)
                if not isinstance(_data, dict):
                    logger.error("feedback id {0} not exists".format(self._id))
                    self._data = {}
                    return None
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]
                
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data