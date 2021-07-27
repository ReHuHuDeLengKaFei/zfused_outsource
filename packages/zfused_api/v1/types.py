# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)

def new_project_type(project_id, entity_type, type_id, active = "true"):
    """ create peoject type

    """
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    # asset is exists
    _types = zfused_api.zFused.get( "project_type", 
                                    filter = { "ProjectId": project_id, 
                                               "Object": entity_type,
                                               "TypeId": type_id })
    if _types:
        return "project type id {} is exists".format(type_id), False

    _create_by_id = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post( key = "project_type", 
                                              data = { "ProjectId": project_id,
                                                       "TypeId": type_id,
                                                       "Object": entity_type,
                                                       "Active": active,
                                                       "CreatedBy": _create_by_id,
                                                       "CreatedTime": _current_time }  )
    if _status:
        return _value["Id"], True
    
    return "project type id create error", False


class ProjectType(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ProjectType, self).__init__("project_type", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("project_type", self._id)
                if not _data:
                    logger.error("project type id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

class Types(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Types, self).__init__("type", entity_id, entity_data)

# class Types(zfused_api.zFused):
#     global_dict = {}
#     def __init__(self, id, data=None):
#         self._id = id
#         self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("type", self._id)
                if not _data:
                    logger.error("type id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def color(self):
        """ return color
        """
        return self._data.get("Color")

    def sort(self):
        return self._data["Sort"]