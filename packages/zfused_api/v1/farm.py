# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function, unicode_literals

import ast
import json
import logging
import datetime

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)




class Farm(_Entity):
    global_dict = {}

    # @classmethod
    # def new(cls, name, code, status_id, color, description = ""):
    #     _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    #     _created_by = zfused_api.zFused.USER_ID

    #     _farms = zfused_api.zFused.get( "farm", filter = {"Code": code})
    #     if _farms:
    #         return "{} is exists".format(name), False

    #     _farm, _status = zfused_api.zFused.post( key = "farm", 
    #                                             data = { "Name": name,
    #                                                      "Code": code,
    #                                                      "StatusId": status_id,
    #                                                      "IsOutsource": 0,
    #                                                      "Priority": 0,
    #                                                      "CreatedBy": _created_by,
    #                                                      "CreatedTime": _created_time } )
    #     if not _status:
    #         return "{} create error".format(name), False

    #     _farm_id = _farm.get("Id")
        
    #     _farm_profile, _status = zfused_api.zFused.post( key = "farm_profile", 
    #                                                 data = { "ProjectId": _farm_id, 
    #                                                         "Color": color,
    #                                                         "Introduction": description,
    #                                                         "CreatedBy": _created_by,
    #                                                         "CreatedTime": _created_time  } )
    #     if not _status:
    #         zfused_api.zFused.delete( "farm", _farm_id )
    #         return "{} create error".format(name), False

    #     _farm_profile_id = _farm_profile.get("Id")

    #     _farm_config, _status = zfused_api.zFused.post( key = "farm_config", 
    #                                                 data = { "ProjectId": _farm_id,
    #                                                          "CreatedBy": _created_by,
    #                                                          "CreatedTime": _created_time } )
    #     if not _status:
    #         zfused_api.zFused.delete( "farm", _farm_id )
    #         zfused_api.zFused.delete( "farm_profile", _farm_profile_id )
    #         return "{} create error".format(name), False
    #     # group user
    #     zfused_api.zFused.post( key = "group_user",
    #                             data = { "EntityType": "farm",
    #                                      "EntityId": _farm_id,
    #                                      "UserId": _created_by,
    #                                      "CreatedBy": _created_by,
    #                                      "CreatedTime": _created_time } )
    #     return _farm_id, True

    def __init__(self, entity_id, entity_data = None):
        super(Farm, self).__init__("farm", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("farm", self._id)
                if not _data:
                    logger.error("farm id {0} not exists".format(self._id))
                    return 
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]


    def title(self):
        return "{} - {}".format(self.name(), self.code())

    @_Entity._recheck
    def ip(self):
        return self._data.get("Ip")

    @_Entity._recheck
    def port(self):
        return self._data.get("Port")

    @_Entity._recheck
    def temp_path(self):
        return self._data.get("TempPath")

    @_Entity._recheck
    def job_info(self):
        _info = self._data.get("JobInfo")
        if _info:
            return eval(_info)
        return {}

    @_Entity._recheck
    def plugin_info(self):
        _info = self._data.get("PluginInfo")
        if _info:
            return eval(_info)
        return {}