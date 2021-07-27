# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)

__all__ = ["Page"]

# zfused_api.page.new_page( _project_id, _name, _code, _status_id, is_outsource = 0, description = _description )
def new_page(name, code, project_id, entity_type, description = ""):
    """ 创建新的标签
    """
    _is_exist = zfused_api.zFused.get("page", filter = { "Name": name, 
                                                         "code": code,
                                                         "ProjectId": project_id,
                                                         "EntityType": entity_type })
    if _is_exist:
        return "{} {} exists".format(name, code), False
    _create_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _create_by = zfused_api.zFused.USER_ID
    _value, _status = zfused_api.zFused.post( key = "page", data = { "Type": "zfused.data.entity.page",
                                                   "Name": name,
                                                   "Code": code,
                                                   "ProjectId": project_id,
                                                   "CreatedBy": _create_by,
                                                   "CreatedTime": _create_time,
                                                   "Description": description,
                                                   "EntityType": entity_type } )
    # _is_exist = zfused_api.zFused.get("page", filter = { "Name": name, 
    #                                                      "Code": code,
    #                                                      "EntityType": entity_type })
    if _status:
        return _value["Id"], True
    return "{} {} create error".format(name, code), False

def tag_link(tag_id, link_object, link_id):
    _is_exist = zfused_api.zFused.get("tag_link", filter = { "TagId": tag_id, 
                                                             "LinkObject": link_object,
                                                             "LinkId": link_id })
    if _is_exist:
        return "{} {} {} exists".format(tag_id, link_object, link_id), False
    _submit_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _submitter_id = zfused_api.zFused.USER_ID
    zfused_api.zFused.post(key = "tag_link", data = { "TagId": tag_id, 
                                                      "LinkObject": link_object,
                                                      "LinkId": link_id ,
                                                      "SubmitterId": _submitter_id,
                                                      "SubmitTime": _submit_time } )
    _tag_links = zfused_api.zFused.get("tag_link", filter = { "TagId": tag_id, 
                                                             "LinkObject": link_object,
                                                             "LinkId": link_id })
    if _tag_links:
        return _tag_links[-1]["Id"], True
    return "{} {} {} exists".format(tag_id, link_object, link_id), False


class Page(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Page, self).__init__("page", entity_id, entity_data)

# class Page(zfused_api.zFused):
#     global_dict = {}
#     def __init__(self, id, data=None):
#         self._id = id
#         self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("page", self._id)
                if not _data:
                    logger.error("page id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    # def object(self):
    #     return "tag"

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
    #     return u"{}({})".format(self.name(), self.code())