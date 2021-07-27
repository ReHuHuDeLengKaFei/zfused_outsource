# coding:utf-8
# --author-- lanhua.zhou

""" 外包商操作api
"""
from __future__ import print_function

import logging
import datetime

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def all_outsourcers(is_active=True):
    """ get all users in zfused

    """
    posts = zfused_api.zFused.get("company") # sortby=["index"], order=["asc"]
    if posts:
        return zfused_api.zFused.get("company", filter={"Id__in": "|".join(["{}".format(_post["Id"]) for _post in posts])})
    return []


class Outsourcer(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Outsourcer, self).__init__("company", entity_id, entity_data)

# class Outsourcer(zfused_api.zFused):
#     global_dict = {}
#     def __init__(self, id, data = None):
#         self._id = id
#         self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("company", self._id)
                if not _data:
                    logger.error("company id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    # def object(self):
    #     return "company"

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
    #     """
    #     get name code

    #     rtype: str
    #     """ 
    #     return u"{}({})".format(self.name(),self.code())

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