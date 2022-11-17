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




class Single(_Entity):

    @classmethod
    def new(cls, name, user_ids):
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        user_ids.sort()
        _code = "_".join([str(_user_id) for _user_id in user_ids])
        _is_has = zfused_api.zFused.get("chat_single", filter = {"Code": _code})
        if _is_has:
            return _is_has[0].get("Id"), True

        _group, _status = zfused_api.zFused.post( key = "chat_single", 
                                                  data = { "Name": name,
                                                           "Code": _code,
                                                           "CreatedBy": _created_by,
                                                           "CreatedTime": _created_time } )
        if not _status:
            return u"{} create error".format(name), False

        _group_id = _group.get("Id")

        # group user
        for _user_id in user_ids:
            zfused_api.zFused.post( "group_user", { "EntityType": "chat_single", 
                                                    "EntityId": _group_id, 
                                                    "UserId": _user_id,
                                                    "CreatedBy": _created_by,
                                                    "CreatedTime": _created_time })

        return _group_id, True


    @classmethod
    def get_from_user_ids(cls, user_ids):
        user_ids.sort()
        _code = "_".join([str(_user_id) for _user_id in user_ids])
        _is_has = zfused_api.zFused.get("chat_single", filter = {"Code": _code})
        if _is_has:
            return cls(_is_has[0].get("Id"))
        return None

    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Single, self).__init__("chat_single", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("chat_single", self._id)
                if not isinstance(_data, dict):
                    logger.error("chat_single id {0} not exists".format(self._id))
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
        return [int(_user_id) for _user_id in self.code().split("_")]





class Group(_Entity):

    @classmethod
    def new(cls, name, user_ids):
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        user_ids.sort()
        _code = "_".join([str(_user_id) for _user_id in user_ids])
        _is_has = zfused_api.zFused.get("chat_group", filter = {"Code": _code})
        if _is_has:
            return _is_has[0].get("Id"), True

        _group, _status = zfused_api.zFused.post( key = "chat_group", 
                                                  data = { "Name": name,
                                                           "Code": _code,
                                                           "CreatedBy": _created_by,
                                                           "CreatedTime": _created_time } )
        if not _status:
            return u"{} create error".format(name), False

        _group_id = _group.get("Id")

        # group user
        for _user_id in user_ids:
            zfused_api.zFused.post( "group_user", { "EntityType": "chat_group", 
                                                    "EntityId": _group_id, 
                                                    "UserId": _user_id,
                                                    "CreatedBy": _created_by,
                                                    "CreatedTime": _created_time })

        return _group_id, True

    
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Group, self).__init__("chat_group", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("chat_group", self._id)
                if not isinstance(_data, dict):
                    logger.error("chat_group id {0} not exists".format(self._id))
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
        pass
