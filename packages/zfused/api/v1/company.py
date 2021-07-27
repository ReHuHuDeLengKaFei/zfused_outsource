# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)

class Company(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Company, self).__init__("company", entity_id, entity_data)

# class Company(zfused_api.zFused):
#     global_dict = {}
#     def __init__(self, id, data=None):
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

    def object(self):
        return "company"

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
        """
        get name code

        rtype: str
        """
        return u"{}({})".format(self.name(), self.code())