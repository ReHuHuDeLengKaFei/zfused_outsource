# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api


def new_file(link_obj, link_id, file_path, index = 0):
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    #get name exists
    _files = zfused_api.zFused.get("files", filter = { "LinkObject": link_obj, 
                                                       "LinkId": link_id, 
                                                       "Index": index, 
                                                       "FilePath": file_path} )
    if _files:
        return True
    _value, _status = zfused_api.zFused.post("files", data = { "LinkObject": link_obj, 
                                             "LinkId": link_id, 
                                             "Index": index, 
                                             "FilePath": file_path,
                                             "CreatedBy": zfused_api.zFused.USER_ID,
                                             "CreatedTime": _current_time } )
    # _files = zfused_api.zFused.get("files", filter = { "LinkObject": link_id, 
    #                                                    "LinkId": link_id, 
    #                                                    "Index": index, 
    #                                                    "FilePath": file_path} )
    if _status:
        return _value["Id"], "files create success"
    return False,"files create error"