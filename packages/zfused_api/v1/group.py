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


def cache(project_id = []):
    """ init project versions
    """
    FeedBack.global_dict = {}
    if not project_id:
        _groups = zfused_api.zFused.get("group", sortby = ["Id"], order = ["desc"])
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _groups = zfused_api.zFused.get("group", filter = {"ProjectId__in": _project_ids}, sortby = ["Id"], order = ["desc"])
    if _groups:
        list(map(lambda _group: FeedBack.global_dict.setdefault(_group["Id"],_group), _groups))
    return _groups

def cache_from_ids(ids):
    ids = "|".join(map(str, ids))
    _groups = zfused_api.zFused.get("group", filter = {"Id__in": ids})
    if _groups:
        list(map(lambda _group: FeedBack.global_dict.setdefault(_group["Id"],_group), _groups))
    return _groups


def get_single(user_ids):
    user_ids.sort()
    _code = "|".join([str(_user_id) for _user_id in user_ids])
    return 

class Group(_Entity):

    @classmethod
    def new(cls, name, user_ids, mode = 0):
        """
        0 single chat
        1 group chat
        """
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        user_ids.sort()
        _code = "|".join([str(_user_id) for _user_id in user_ids])
        _is_has = zfused_api.zFused.get("group", filter = {"Code": _code, "Mode": mode})
        if _is_has:
            return _is_has[0].get("Id"), True

        _group, _status = zfused_api.zFused.post( key = "group", 
                                                  data = { "Name": name,
                                                           "Code": _code,
                                                           "Mode": mode,
                                                           "CreatedBy": _created_by,
                                                           "CreatedTime": _created_time } )
        if not _status:
            return u"{} create error".format(name), False

        _group_id = _group.get("Id")

        # group user
        for _user_id in user_ids:
            zfused_api.zFused.post( "group_user", { "EntityType": "group", 
                                                    "EntityId": _group_id, 
                                                    "UserId": _user_id,
                                                    "CreatedBy": _created_by,
                                                    "CreatedTime": _created_time })

        return _group_id, True

    
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Group, self).__init__("group", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("group", self._id)
                if not isinstance(_data, dict):
                    logger.error("group id {0} not exists".format(self._id))
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

    def add_user_id(self, user_id):
        pass

    def remove_user_id(self, user_id):
        pass

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