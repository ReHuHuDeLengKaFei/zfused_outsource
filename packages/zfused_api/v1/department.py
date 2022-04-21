# coding:utf-8
# --author-- lanhua.zhou

""" 职位操作api
"""
from __future__ import print_function

import logging
import datetime

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def all_departments(is_active=True):
    """ get all users in zfused

    """
    return zfused_api.zFused.get("department", sortby=["Id"], order=["asc"])
    # if posts:
    #     return zfused_api.zFused.get("department", filter={"Id__in": "|".join(["{}".format(_post["Id"]) for _post in posts])})
    # return []

def new_department(name, code, parent_id = 0):
    # asset is exists
    _departments = zfused_api.zFused.get( "department", 
                                          filter = {"name": name, "code": code, "pid": parent_id})
    if _departments:
        return "{} is exists".format(name), False

    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _created_by = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post(key = "department", data = { "Name": name,
                                                                     "Code": code,
                                                                     "Pid": parent_id,
                                                                     "Sort": 0,
                                                                     "CreateTime": _current_time,
                                                                     "Active": "true",
                                                                     "CreatedBy":_created_by,
                                                                     "CreatedTime":_current_time })
    if _status:
        return Department(_value["Id"], _value), True
    return "{} create error".format(name), False


class Department(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Department, self).__init__("department", entity_id, entity_data)

# class Department(zfused_api.zFused):
#     global_dict = {}
#     def __init__(self, id, data = None):
#         self._id = id
#         self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("department", self._id)
                if not _data:
                    logger.error("department id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def object(self):
        return "department"

    def id(self):
        return self._id

    def data(self):
        return self._data

    def code(self):
        """
        get code

        rtype: str
        """
        return u"{}".format(self._data["Code"])   

    def name(self):
        """
        get name

        rtype: str
        """
        return u"{}".format(self._data["Name"])

    def name_code(self):
        """ get name code

        rtype: str
        """ 
        return u"{}({})".format(self.name(),self.code())

    def full_code(self):
        """ get full path code

        rtype: str
        """
        _pid = self._data["Pid"]
        if _pid:
            _p_handle = Department(_pid)
            return "{}|{}".format(_p_handle.full_name(), self._data["Code"])
        return self._data["Code"]

    def full_name(self):
        """ get full path name

        rtype: str
        """
        _pid = self._data["Pid"]
        if _pid:
            _p_handle = Department(_pid)
            return "{}|{}".format(_p_handle.full_name(), self._data["Name"])
        return self._data["Name"]

    def full_name_code(self):
        """ get full path name and code

        rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())

    def users_count(self):
        """ get users count

        rtyle: list
        """
        _users = self.get("department_user", filter={"DepartmentId": self._id})
        if _users:
            return len(_users)
        return 0

    def users_id(self):
        _users = self.get("department_user", filter={"DepartmentId": self._id})
        if _users:
            _users_id = [_user["UserId"] for _user in _users]
            return _users_id
        return []

    def user_ids(self):
        _users = self.get("department_user", filter={"DepartmentId": self._id})
        if _users:
            _users_id = [_user["UserId"] for _user in _users]
            return _users_id
        return []

    def add_user(self, user_id):
        """ add user to department
        """
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _department_user = self.get("department_user", filter = {"DepartmentId":self._id, "UserId":user_id})
        if _department_user:
            return False, "department has user {}".format(user_id)
        self.post("department_user", data = { "DepartmentId":self._id, 
                                              "UserId":user_id,
                                              "CreateTime": _current_time,
                                              "Active": "true",
                                              "CreatedBy": self.USER_ID,
                                              "CreatedTime": _current_time })
        _department_user = self.get("department_user", filter = {"DepartmentId":self._id, "UserId":user_id})
        if _department_user:
            return True, "department user create success"
        return False,"department user create error"

    def remove_user(self, user_id):
        """ remove department user
        """
        # get department user key id
        _department_users = self.get("department_user", filter = {"DepartmentId":self._id, "UserId":user_id})
        if _department_users:
            for _department_user in _department_users:
                self.delete("department_user", _department_user["Id"])