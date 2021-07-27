# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import datetime

from . import _Entity
import zfused_api

def new(name, code, entity_type, color, description):
    _categorys = zfused_api.zFused.get( "category", filter = {"Code": code})
    if _categorys:
        return "{} is exists".format(name), False
    _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _created_by = zfused_api.zFused.USER_ID
    _category, _status = zfused_api.zFused.post(key = "category", data = { "Name": name,
                                                                           "Code": code,
                                                                           "EntityType": entity_type,
                                                                           "color": color,
                                                                           "Description":description,
                                                                           "CreatedBy":_created_by,
                                                                           "CreatedTime":_created_time })
    if _status:
        return _category["Id"], True
    return "{} create error".format(name), False

class Category(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Category, self).__init__("category", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("category", self._id)
                if not _data:
                    logger.error("category id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def color(self):
        return self._data["Color"]