# coding:utf-8
# --author-- lanhua.zhou

"""
    relative 
"""

from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)

def create_relatives(src_obj, src_id, dst_obj, dst_id, relatioon_ship = "reference", name_space = "", active = 'true'):
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    #get name exists
    # _relatives = zfused_api.zFused.get("relative", filter = { "SourceObject": src_obj, 
    #                                                           "SourceId": src_id, 
    #                                                           "TargetObject": dst_obj, 
    #                                                           "TargetId": dst_id, 
    #                                                           "Relationship": relatioon_ship,
    #                                                           "NameSpace": name_space })

    _value, _status = zfused_api.zFused.post(key = "relative", data = { "SourceObject": src_obj, 
                                                                        "SourceId": src_id, 
                                                                        "TargetObject": dst_obj, 
                                                                        "TargetId": dst_id, 
                                                                        # "CreateTime": _current_time, 
                                                                        "Relationship": relatioon_ship,
                                                                        "NameSpace": name_space,
                                                                        "Active": active,
                                                                        "CreatedBy": zfused_api.zFused.USER_ID,
                                                                        "CreatedTime": _current_time } )

    # _relatives = zfused_api.zFused.get("relative", filter = { "SourceObject": src_obj, 
    #                                                           "SourceId": src_id, 
    #                                                           "TargetObject": dst_obj, 
    #                                                           "TargetId": dst_id,
    #                                                           "Relationship": relatioon_ship,
    #                                                           "NameSpace": name_space })
    
    if _value:
        return True, "relative create success"
    return False,"relative create error"


def clear_relatives(dst_object, dst_id):
    """ clear src obj relatives

    """
    # get relatives
    _relatives = zfused_api.zFused.get("relative", filter = {"TargetObject": dst_object, 
                                                      "TargetId": dst_id})
    if _relatives:
        # 数据库删除 。。。
        for _relative in _relatives:
            zfused_api.zFused.delete("relative", _relative["Id"])
    return True

def get_relatives(obj, obj_id):
    """ get obj relatives

    """
    _relatives = []
    _relatives += zfused_api.zFused.get("relative", filter = {"SourceObject": obj, 
                                                      "SourceId": obj_id})
    _relatives += zfused_api.zFused.get("relative", filter = {"TargetObject": obj, 
                                                       "TargetId": obj_id})
    return _relatives


def relatives(obj, obj_id):
    """ get obj relatives

    """
    _relatives = []
    _relatives += zfused_api.zFused.get("relative", filter = {"SourceObject": obj, 
                                                              "SourceId": obj_id})
    _relatives += zfused_api.zFused.get("relative", filter = {"TargetObject": obj, 
                                                              "TargetId": obj_id})
    return _relatives
