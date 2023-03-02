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
    """ get logins 
        init 
    """
    _s_t = time.time()
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])
    if not project_ids:
        _logins = zfused_api.zFused.get("login", filter = {"StatusId__in": _status_ids} )
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_ids])
        _logins = zfused_api.zFused.get("login", filter = {"ProjectId__in": _project_ids, "StatusId__in": _status_ids})
    if _logins:
        list(map(lambda _login: Login.global_dict.setdefault(_login["Id"],_login), _logins))
    _e_t = time.time()
    logger.info("login cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _loginsLogin

def cache_from_ids(ids, extract_freeze = True):
    _s_t = time.time()
    if extract_freeze:
        _status_ids = zfused_api.zFused.get("status", fields = ["Id"])
    else:
        _status_ids = zfused_api.zFused.get("status", filter = {"IsFreeze": 0}, fields = ["Id"])
    _status_ids = "|".join([str(_status_id["Id"]) for _status_id in _status_ids])
    ids = "|".join(map(str, ids))
    _logins = zfused_api.zFused.get("login", filter = {"Id__in": ids, "StatusId__in": _status_ids})
    if _logins:
        list(map(lambda _login: Login.global_dict.setdefault(_login["Id"],_login), _logins))
    _e_t = time.time()
    logger.info("login cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _logins



class Login(_Entity):


    @classmethod
    def new(cls, project_id, project_step_id, title, user_ids, thumbnail_path, description = ""):
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        # _task = zfused_api.task.Task(task_id)
        _status_id = zfused_api.status.active_status_ids()[0]

        _login, _status = zfused_api.zFused.post( key = "login", 
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

        _login_id = _login.get("Id")

        # group user
        for _user_id in user_ids:
            zfused_api.zFused.post( "group_user", { "EntityType": "login", 
                                        "EntityId": _login_id, 
                                        "UserId": _user_id,
                                        "CreatedBy": _created_by,
                                        "CreatedTime": _created_time })

        zfused_api.im.submit_message( "user",
                                      _created_by,
                                      user_ids,
                                      {"entity_type": "login",
                                       "entity_id": _login_id},
                                      "login", 
                                      "login",
                                      _login_id,
                                      "login",
                                      _login_id )

        return _login_id, True


    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Login, self).__init__("login", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("login", self._id)
                if not _data:
                    logger.error("login id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def object(self):
        return "login"

    def title(self):
        return self.name()

    def name_code(self):
        return self.name()

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
        v = self.put("login", self._data["Id"], self._data, "status_id")
        if v:
            return True
        else:
            return False

    def user_id(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("UserId")

    def user(self):
        return zfused_api.user.User(self.user_id())
    
    def description(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("Description")

    def update_description(self, _description):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        self.global_dict[self._id]["Description"] = _description
        self._data["Description"] = _description
        v = self.put("login", self._data["Id"], self._data, "description")
        if v:
            return True
        else:
            return False

    def thumbnail(self):
        """ get thumbnai name
        """
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self.global_dict[self._id]["Thumbnail"]

    def get_thumbnail(self, is_version = False):
        return self.user().get_thumbnail()

    def ip(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("Ip")
    
    def port(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("Port")

    def app_name(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("AppName")

    def app_version(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("AppVersion")
    
    def machine_name(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("MachineName")

    def machine_user(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        return self._data.get("MachineUser")
    
    def online_time(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data

        _time_text = self._data["OnlineTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

    def offline_time(self):
        if not isinstance(self._data, dict):
            self._data = self.get_one(self._type, self._id)
            self.global_dict[self._id] = self._data
            
        _time_text = self._data["OfflineTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")