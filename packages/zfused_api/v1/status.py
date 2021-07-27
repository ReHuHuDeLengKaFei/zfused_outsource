# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime

from . import _Entity
import zfused_api


def new_project_status(project_id, entity_type, status_id, active = "true"):
    """ create peoject status

    """
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    # asset is exists
    _status = zfused_api.zFused.get( "project_status", 
                                    filter = { "ProjectId": project_id, 
                                               "Object": entity_type,
                                               "StatusId": status_id })
    if _status:
        return "project status id {} is exists".format(status_id), False

    _create_by_id = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post( key = "project_status", 
                                              data = { "ProjectId": project_id,
                                                       "StatusId": status_id,
                                                       "Object": entity_type,
                                                       "Active": active,
                                                       "CreatedBy": _create_by_id,
                                                       "CreatedTime": _current_time }  )
    if _status:
        return _value["Id"], True
    
    return "project status id create error", False

def active_status():
    """
    获取激活可制作的任务

    """
    _active_status = zfused_api.zFused.get("status", filter = {"IsActive":1}, sortby = ["Sort"], order = ["asc"])
    if _active_status:
        return [Status(_status["Id"]) for _status in _active_status]
    return []

def active_status_ids():
    """
    获取激活可制作的任务

    """
    _active_status = zfused_api.zFused.get("status", filter = {"IsActive":1}, sortby = ["Sort"], order = ["asc"])
    if _active_status:
        return [_status["Id"] for _status in _active_status]
    return []

def working_status():
    """
    获取制作中的状态标签

    """
    _working_status = zfused_api.zFused.get("status", filter = {"IsWorking":1}, sortby = ["Sort"], order = ["asc"])
    if _working_status:
        return [Status(_status["Id"]) for _status in _working_status]
    return []

def working_status_ids():
    """
    获取制作中的状态id
    """
    _woking_status = zfused_api.zFused.get("status", filter = {"IsWorking":1}, sortby = ["Sort"], order = ["asc"])
    if _woking_status:
        return [_status["Id"] for _status in _woking_status]
    return []

def waiting_status():
    """ 获取等待任务

    """
    _waiting_status = zfused_api.zFused.get("status", filter = {"IsWaiting":1}, sortby = ["Sort"], order = ["asc"])
    if _waiting_status:
        return [Status(_status["Id"]) for _status in _waiting_status]
    return []

def waiting_status_ids():
    """ 获取等待任务id

    """
    _waiting_status = zfused_api.zFused.get("status", filter = {"IsWaiting":1}, sortby = ["Sort"], order = ["asc"])
    if _waiting_status:
        return [_status["Id"] for _status in _waiting_status]
    return []

def final_status():
    """ 获取完结状态

    """
    _final_status = zfused_api.zFused.get("status", filter = {"IsFinal":1}, sortby = ["Sort"], order = ["asc"])
    if _final_status:
        return [Status(_status["Id"]) for _status in _final_status]
    return []

def final_status_ids():
    """ 获取完结状态

    """
    _final_status = zfused_api.zFused.get("status", filter = {"IsFinal":1}, sortby = ["Sort"], order = ["asc"])
    if _final_status:
        return [_status["Id"] for _status in _final_status]
    return []

def done_status_ids():
    """ 获取完结状态
    """ 
    _final_status = zfused_api.zFused.get("status", filter = {"Category":"done"}, sortby = ["Sort"], order = ["asc"])
    if _final_status:
        return [_status["Id"] for _status in _final_status]
    return []

def review_status():
    """ 获取完结状态

    """
    _final_status = zfused_api.zFused.get("status", filter = {"IsReview":1}, sortby = ["Sort"], order = ["asc"])
    if _final_status:
        return [Status(_status["Id"]) for _status in _final_status]
    return []

def review_status_ids():
    """ 获取完结状态

    """
    _final_status = zfused_api.zFused.get("status", filter = {"IsReview":1}, sortby = ["Sort"], order = ["asc"])
    if _final_status:
        return [_status["Id"] for _status in _final_status]
    return []

def approval_status():
    """ 获取完结状态

    """
    _final_status = zfused_api.zFused.get("status", filter = {"IsApproval":1}, sortby = ["Sort"], order = ["asc"])
    if _final_status:
        return [Status(_status["Id"]) for _status in _final_status]
    return []

def approval_status_ids():
    """ 获取完结状态

    """
    _final_status = zfused_api.zFused.get("status", filter = {"IsApproval":1}, sortby = ["Sort"], order = ["asc"])
    if _final_status:
        return [_status["Id"] for _status in _final_status]
    return []

def status_ids():
    """
    获取所有状态id
    """
    _status = zfused_api.zFused.get("status", sortby = ["Sort"], order = ["asc"])
    if _status:
        return [_statu["Id"] for _statu in _status]
    return []


def cache_from_ids(status_ids = []):
    status_ids = [str(_status_id) for _status_id in status_ids]
    _status = zfused_api.zFused.get("status", filter = {"Id__in": "|".join(status_ids)}, sortby = ["Sort"], order = ["asc"])
    if _status:
        return _status
    return []

class Status(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Status, self).__init__("status", entity_id, entity_data)

# class Status(zfused_api.zFused):
#     global_dict = {}
#     def __init__(self, id, data = None):
#         self._id = id
#         self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("status", self._id)
                if not _data:
                    logger.error("status id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def full_code(self):
        """
        get full path code

        rtype: str
        """
        return self._data["Code"]

    def full_name(self):
        """
        get full path name

        rtype: str
        """
        return self._data["Name"]


    def full_name_code(self):
        """
        get full path name and code

        rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())

    def color(self):
        """ return project color

        """
        return self._data["Color"]

    def sort(self):
        return self._data["Sort"]

    def category(self):
        return self._data.get("Category")
