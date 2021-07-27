# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from collections import defaultdict

import hashlib
import logging
import datetime

from . import _Entity
import zfused_api

#from . import status

logger = logging.getLogger(__name__)


def new_user(login_name, login_password, name, code, department = 0, post = 0):
    """ create user

    """
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    # is exist user
    #
    _user = zfused_api.zFused.get("user", filter = {"Username": login_name})
    if _user:
        return False, "has user {}".format(login_name)
    # password
    #
    md5 = hashlib.md5()
    md5.update(login_password.encode("utf8"))
    _password = md5.hexdigest()
    _user, _status = zfused_api.zFused.post("user", data = { "Username": login_name,
                                                              "Password": _password,
                                                              "Active": "true",
                                                              "CreatedBy": zfused_api.zFused.USER_ID,
                                                              "CreatedTime": _current_time })
    if _status:
        _user_id = _user["Id"]
        # create user profile
        # _user = zfused_api.zFused.get("user", filter = {"Username": login_name})[0]
        _user_profile, _status = zfused_api.zFused.post("user_profile", data = { "UserId": _user["Id"],
                                                                                  "Avatar": "",
                                                                                  "NameCn": name,
                                                                                  "NameEn": code,
                                                                                  "Sex": "male",
                                                                                  "Email": "",
                                                                                  "Phone": "",
                                                                                  "Active": "true", 
                                                                                  "CreatedBy": zfused_api.zFused.USER_ID,
                                                                                  "CreatedTime": _current_time })
        if _status:
            # connect department
            if department:
                zfused_api.zFused.post("department_user", data = { "DepartmentId": department,
                                                                        "UserId": _user_id,
                                                                        "CreateTime": _current_time,
                                                                        "Active": "true",
                                                                        "CreatedBy": zfused_api.zFused.USER_ID,
                                                                        "CreatedTime": _current_time })
            # connect post
            if post:
                zfused_api.zFused.post("post_user", data = { "PostId": post,
                                                             "UserId": _user_id,
                                                             "CreatedBy": zfused_api.zFused.USER_ID,
                                                             "CreatedTime": _current_time })

            return _user["Id"], "create new user {} success".format(login_name)

    return False, "create new user {} error".format(login_name)

def all_users(is_active = True):
    """
    get all users in zfused


    """
    if is_active:
        users = zfused_api.zFused.get("user_profile", filter={"Active": "true"}, sortby=["NameEn"], order=["asc"])
    else:
        users = zfused_api.zFused.get("user_profile", sortby=["NameEn"], order=["asc"])
    if users:
        return zfused_api.zFused.get("user", 
                                     filter={"Id__in": "|".join(["{}".format(_user["UserId"]) for _user in users])},
                                     sortby=["Username"], order=["asc"])
    return []

def login(login_name, login_password):
    """
    login zfusde 

    rtype: zfusde.user
    """
    userData = api.Get("user", filter={"Username": name})
    if not userData:
        _log.error("%s is not exists" % name)
        return False, "%s is not exists" % name
    md = hashlib.md5()
    md.update(password)
    if userData[0]["Password"] != md.hexdigest():
        _log.error("password error")
        return False, "password error"
    # test
    cgm.cgm.SetUser(userData[0]["Id"])
    return True, user(userData[0]["Id"])

def cache(user_ids = []):
    """ init cache
    """
    if user_ids:
        _users = zfused_api.zFused.get("user", filter = {"Id__in": "|".join(map(str, user_ids)), "Active":"true"} ,sortby=["Username"], order=["asc"])
        _user_profiles = zfused_api.zFused.get("user_profile", filter = {"UserId__in": "|".join(map(str, user_ids))})
        _post_users = zfused_api.zFused.get("post_user", filter = {"UserId__in": "|".join(map(str, user_ids))})
        _department_users = zfused_api.zFused.get("department_user", filter = {"UserId__in": "|".join(map(str, user_ids))})
    else:
        _users = zfused_api.zFused.get("user", filter = {"Active":"true"}, sortby=["Username"], order=["asc"])
        _user_profiles = zfused_api.zFused.get("user_profile")
        _post_users = zfused_api.zFused.get("post_user")
        _department_users = zfused_api.zFused.get("department_user")

    if _users:
        list(map(lambda _user: User.global_dict.setdefault(_user["Id"], _user), _users))
        # list(map(lambda _user: User.global_post.setdefault(_user["Id"], set([])), _users))
        # list(map(lambda _user: User.global_department.setdefault(_user["Id"], set([])), _users))
    if _user_profiles:
        list(map(lambda _user_profile: User.global_profile.setdefault(_user_profile["UserId"], _user_profile), _user_profiles))
    if _post_users:
        list(map(lambda _post_user: User.global_post[_post_user["UserId"]].add(_post_user["PostId"]), _post_users))
    if _department_users:
        list(map(lambda _department_user: User.global_department[_department_user["UserId"]].add(_department_user["DepartmentId"]), _department_users))
    return _users

def cache_from_ids(user_ids = []):
    """ init cache
    """
    if user_ids:
        _users = zfused_api.zFused.get("user", filter = {"Id__in": "|".join(map(str, user_ids))} ,sortby=["Username"], order=["asc"])
        _user_profiles = zfused_api.zFused.get("user_profile", filter = {"UserId__in": "|".join(map(str, user_ids))})
        _post_users = zfused_api.zFused.get("post_user", filter = {"UserId__in": "|".join(map(str, user_ids))})
        _department_users = zfused_api.zFused.get("department_user", filter = {"UserId__in": "|".join(map(str, user_ids))})

    if _users:
        list(map(lambda _user: User.global_dict.setdefault(_user["Id"], _user), _users))
        # list(map(lambda _user: User.global_post.setdefault(_user["Id"], set([])), _users))
        # list(map(lambda _user: User.global_department.setdefault(_user["Id"], set([])), _users))
    if _user_profiles:
        list(map(lambda _user_profile: User.global_profile.setdefault(_user_profile["UserId"], _user_profile), _user_profiles))
    if _post_users:
        list(map(lambda _post_user: User.global_post[_post_user["UserId"]].add(_post_user["PostId"]), _post_users))
    if _department_users:
        list(map(lambda _department_user: User.global_department[_department_user["UserId"]].add(_department_user["DepartmentId"]), _department_users))
    return _users


class User(_Entity):
    global_dict = {}
    global_profile = {}
    global_post = defaultdict(set)
    global_department = defaultdict(set)
    def __init__(self, entity_id, entity_data = None):
        super(User, self).__init__("user", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            _datas = self.get_one("user", self._id)
            if not _datas:
                logger.error("user id {0} is not exists".format(self._id))
                return
            self._data = _datas
            _profiles = self.get("user_profile", filter={"UserId": self._id})
            if not _profiles:
                logger.error("user id {0} is not exists".format(self._id))
                return
            self.profile = _profiles[0]
            self.global_dict[self._id] = self._data
            self.global_profile[self._id] = self.profile
            self.global_post[self._id] = set(self.post_ids())
            self.global_department[self._id] = set(self.department_ids())
        else:
            self._data = self.global_dict[self._id]
            self.profile = self.global_profile[self._id]
        self._thumbnail = None

    def code(self):
        """
        get full path code

        rtype: str
        """
        if self._id == 0:
            return "none"
        return self.profile["NameEn"]

    def name(self):
        """
        get full path name

        rtype: str
        """
        if self._id == 0:
            return u"无用户"
        return self.profile["NameCn"]

    def name_code(self):
        """
        get full path name and code

        rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())


    def full_code(self):
        """
        get full path code

        rtype: str
        """
        return self.profile["NameEn"]

    def full_name(self):
        """
        get full path name

        rtype: str
        """
        return self.profile["NameCn"]

    def full_name_code(self):
        """
        get full path name and code

        rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())

    # def relation_users(self):
    #     _group_user_list = self.Get("project_user_relation", filter={
    #                                 "SuperiorId": self._id})
    #     if not _group_user_list:
    #         return []
    #     else:
    #         return self.Get("user", filter={"Id__in": "|".join(["{}".format(_user["UserId"]) for _user in _group_user_list])})

    def working_tasks(self):
        """
        获取制作中的任务

        rtyle: list
        """
        _is_working_task = zfused_api.status.working_status_ids()
        _is_working_task = [str(i) for i in _is_working_task]
        _tasks = self.get("task", filter={
                          "AssignedTo": self._id, "StatusId__in": "|".join(_is_working_task)})
        if _tasks:
            # _task_ids = [_task["Id"] for _task in _tasks]
            # zfused_api.objects.cache("task", _task_ids)
            return _tasks
        return []

    def active_tasks(self):
        """ 获取当前用户激活中的任务
        """
        _active_status_ids = zfused_api.status.active_status_ids()
        _active_status_ids = [str(i) for i in _active_status_ids]
        _tasks = self.get("task", filter={  "AssignedTo": self._id, 
                                            "StatusId__in": "|".join(_active_status_ids)} )
        if _tasks:
            # _task_ids = [_task["Id"] for _task in _tasks]
            # zfused_api.objects.cache("task", _task_ids)
            return _tasks
        return []

    '''
    def UpdatePassword(self, password):
        md = hashlib.md5()
        md.update(password)
        ps = md.hexdigest()
        self._data["Password"] = ps
        self.Put("user", self._data["Id"], self._data)
    

    def GetProfile(self):
        return user_profile(self._id)

    def GetTasks(self, filter = {}, fields = [], sortby = [], order = [], offset = None):
        filter_data = filter
        filter_data["AssignedTo"] = self._id
        allTasks = self.Get("task", filter = filter_data, fields = fields, sortby = sortby, order = order, offset = offset)
        return allTasks

    def GetThumbnail(self):
        _thumbnail = self.profile.get("Thumbnail")
        return _thumbnail
    '''

    def thumbnail(self):
        return None

    def get_thumbnail(self):
        # _thumbnail_path = self._data.get("ThumbnailPath")
        # if _thumbnail_path:
        #     if _thumbnail_path.startswith("storage"):
        #         return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        # return None
        _thumbnail = self.profile["Avatar"]
        if _thumbnail.startswith("storage"):
            return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail.split("storage/")[-1])
        return None

    def get_avatar(self):
        _thumbnail = self.profile["Avatar"]
        if _thumbnail.startswith("storage"):
            return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail.split("storage/")[-1])
        return None

    def update_avatar(self, avatar_path):
        self.profile["Avatar"] = avatar_path
        v = self.put("user_profile", self.profile["Id"], self.profile, "avatar")
        if v:
            return True
        else:
            return False

    def relation_users(self):
        _group_user_list = self.get("project_user_relation", filter={
                                    "SuperiorId": self._id})
        if not _group_user_list:
            return []
        else:
            return self.get("user", filter={"Id__in": "|".join(["{}".format(_user["UserId"]) for _user in _group_user_list])})

    def post_ids(self):
        """ get post id
        
        """
        if self._id not in self.global_post:
            _post_users = self.get("post_user", filter = {"UserId":self._id})
            if not _post_users:
                self.global_post[self._id] = []
            else:
                self.global_post[self._id] = [_post_user["PostId"] for _post_user in _post_users]
        return self.global_post[self._id]

    def department_ids(self):
        """ get department id

        """
        if self._id not in self.global_department:
            _department_users = self.get("department_user", filter = {"UserId": self._id})
            if not _department_users:
                self.global_department[self._id] = []
            else:
                self.global_department[self._id] = [_department_user["DepartmentId"] for _department_user in _department_users]
        return self.global_department[self._id]

    def clear_unread_messags(self):
        pass

    def resign(self):
        self.global_dict[self._id]["Active"] = "false"
        self._data["Active"] = "false"
        self.global_profile[self._id]["Active"] = "false"
        v = self.put("user", self._data["Id"], self._data, "active")
        v = self.put("user_profile", self.global_profile[self._id]["Id"], self.global_profile[self._id], "active")
        if v:
            return True
        else:
            return False

    def set_task_times(self, task_times):
        pass

    def new_task_time(self):
        pass

    def task_times(self):
        return 