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


def all_posts(is_active=True):
    """ get all users in zfused

    """
    posts = zfused_api.zFused.get("post", sortby=["index"], order=["asc"])
    if posts:
        return zfused_api.zFused.get("post", filter={"Id__in": "|".join(["{}".format(_post["Id"]) for _post in posts])})
    return []

def new_post(name, code):
    """ add post
    
    """
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    logger.info("create new post")
    _posts = zfused_api.zFused.get("post", filter = {"Name": name, "Code": code})
    if _posts:
        return _posts[0], False
    zfused_api.zFused.post("post", data = { "Name": name, 
                                            "Code": code, 
                                            "Level": 0,
                                            "Index": 0,
                                            # "CreateTime": _current_time,
                                            "Color:": "",
                                            "Description": "",
                                            "Active": "true",
                                            "CreatedBy": zfused_api.zFused.USER_ID,
                                            "CreatedTime": _current_time  })
    return None, True

def remove_post(post_id):
    """ remove post

    """
    # get post user
    _post_user = zfused_api.zFused.get("post_user", filter = {"PostId": post_id})
    if _post_user:
        return "has user in post", False
    _v = zfused_api.zFused.delete("post", post_id)
    if _v:
        return "success", _v


class Post(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Post, self).__init__("post", entity_id, entity_data)

# class Post(zfused_api.zFused):
#     global_dict = {}
#     def __init__(self, id, data = None):
#         self._id = id
#         self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("post", self._id)
                if not _data:
                    logger.error("post id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    # def object(self):
    #     return "post"

    # def id(self):
    #     return self._id

    # def data(self):
    #     return self._data

    # def code(self):
    #     """
    #     get code

    #     rtype: str
    #     """
    #     return u"{}".format(self._data["Code"])   

    # def name(self):
    #     """
    #     get name

    #     rtype: str
    #     """
    #     return u"{}".format(self._data["Name"])

    # def name_code(self):
    #     """ get name code

    #     rtype: str
    #     """ 
    #     return u"{}({})".format(self.name(),self.code())

    def full_code(self):
        """ get full path code

        rtype: str
        """
        return self._data["Code"]

    def full_name(self):
        """ get full path name

        rtype: str
        """
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
        _users = self.get("post_user", filter={"PostId": self._id})
        if _users:
            return len(_users)
        return 0

    def users_id(self):
        _users = self.get("post_user", filter={"PostId": self._id})
        if _users:
            _users_id = [_user["UserId"] for _user in _users]
            return _users_id
        return []

    def add_user(self, user_id):
        """ add user to post
        
        """
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _post_user = self.get("post_user", filter = {"PostId":self._id, "UserId":user_id})
        if _post_user:
            return False, "post has user {}".format(user_id)
        _post_user, _status = self.post("post_user", data = { "PostId":self._id, 
                                                              "UserId":user_id,
                                                              "CreatedBy": zfused_api.zFused.USER_ID,
                                                              "CreatedTime": _current_time  })
        # _post_user = self.get("post_user", filter = {"PostId":self._id, "UserId":user_id})
        if _status:
            return True, "post user create success"
        return False,"post user create error"

    def remove_user(self, user_id):
        """ remove post user
        
        """
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # get post user key id
        _post_users = self.get("post_user", filter = { "PostId":self._id, "UserId":user_id})
        if _post_users:
            for _post_user in _post_users:
                self.delete("post_user", _post_user["Id"])