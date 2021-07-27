# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)

__all__ = ["Tag"]


def new_tag(name, code, color, link_object = "all"):
    """ 创建新的标签
    """
    _is_exist = zfused_api.zFused.get("tag", filter = { "Name": name, 
                                                        "code": code })
    if _is_exist:
        return "{} {} exists".format(name, code), False
    _submit_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _submitter_id = zfused_api.zFused.USER_ID
    _tag, _status = zfused_api.zFused.post(key = "tag", data = { "Name": name,
                                                                 "Code": code,
                                                                 "Color": color,
                                                                 "LinkObject": link_object,
                                                                 "SubmitterId": _submitter_id,
                                                                 "SubmitTime": _submit_time,
                                                                 "CreatedBy": zfused_api.zFused.USER_ID,
                                                                 "CreatedTime": _submit_time } )
    if _status:
        return _tag["Id"], True
    return "{} {} create error".format(name, code), False

def tag_link(tag_id, link_object, link_id):
    _is_exist = zfused_api.zFused.get("tag_link", filter = { "TagId": tag_id, 
                                                             "LinkObject": link_object,
                                                             "LinkId": link_id })
    if _is_exist:
        return "{} {} {} exists".format(tag_id, link_object, link_id), False
    _submit_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _submitter_id = zfused_api.zFused.USER_ID
    _tag_link, _err = zfused_api.zFused.post(key = "tag_link", data = { "TagId": tag_id, 
                                                                        "LinkObject": link_object,
                                                                        "LinkId": link_id ,
                                                                        "SubmitterId": _submitter_id,
                                                                        "SubmitTime": _submit_time,
                                                                        "CreatedBy": _submitter_id,
                                                                        "CreatedTime": _submit_time } )
    if _err:
        return _tag_link["Id"], True
    return "{} {} {} exists".format(tag_id, link_object, link_id), False


class Tag(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Tag, self).__init__("tag", entity_id, entity_data)
        
        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("tag", self._id)
                if not _data:
                    logger.error("tag id {0} not exists".format(self._id))
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