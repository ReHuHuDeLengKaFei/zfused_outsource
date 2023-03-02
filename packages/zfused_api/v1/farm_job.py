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




class FarmJob(_Entity):
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
        super(FarmJob, self).__init__("farm_job", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("farm_job", self._id)
                if not _data:
                    logger.error("farm_job id {0} not exists".format(self._id))
                    return 
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    @_Entity._recheck
    def title(self):
        return "{} - {}".format(self.name(), self.code())

    @_Entity._recheck
    def status(self):
        return self._data.get("Status")

    @_Entity._recheck
    def farm_id(self):
        return self._data.get("FarmId")

    @_Entity._recheck
    def farm(self):
        return zfused_api.farm.Farm(self._data.get("FarmId"))

    @_Entity._recheck
    def job_id(self):
        return self._data.get("JobId")

    @_Entity._recheck
    def task_id(self):
        return self._data.get("TaskId")

    @_Entity._recheck
    def task(self):
        return zfused_api.task.Task(self.task_id())

    @_Entity._recheck
    def project_entity_type(self):
        return self._data.get("ProjectEntityType")
    
    @_Entity._recheck
    def project_entity_id(self):
        return self._data.get("ProjectEntityId")

    @_Entity._recheck
    def project_entity(self):
        _project_entity_type = self.project_entity_type()
        _project_entity_id = self.project_entity_id()
        if _project_entity_type == "asset":
            return zfused_api.asset.Asset(_project_entity_id)
        elif _project_entity_type == "assembly":
            return zfused_api.assembly.Assembly(_project_entity_id)
        elif _project_entity_type == "episode":
            return zfused_api.episode.Episode(_project_entity_id)
        elif _project_entity_type == "sequence":
            return zfused_api.sequence.Sequence(_project_entity_id)
        elif _project_entity_type == "shot":
            return zfused_api.shot.Shot(_project_entity_id)
        return zfused_api.objects.Objects(self._data["ProjectEntityType"], self._data["ProjectEntityId"])

    @_Entity._recheck
    def project_step_id(self):
        return self._data.get("ProjectStepId")

    @_Entity._recheck
    def project_step(self):
        return zfused_api.step.ProjectStep(self.project_step_id())

    def get_thumbnail(self):
        return self.task().get_thumbnail()

    @_Entity._recheck
    def update_status(self, status):
        if self._data.get("Status") == status:
            return 
        self.global_dict[self._id]["Status"] = status
        self._data["Status"] = status
        v = self.put("farm_job", self._data["Id"], self._data, "status")
        if v:
            return True
        else:
            return False