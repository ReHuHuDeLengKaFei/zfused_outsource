# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api


def new_file(md5, path, name, format, suffix, size, thumbnail_path = "", width = 0, height = 0):
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    #get name exists
    _files = zfused_api.zFused.get("file", filter = { "MD5": md5} )
    if _files:
        return True, "file is has"
    _value, _status = zfused_api.zFused.post( "file", data = { "MD5": md5, 
                                             "Type": "entity.file",
                                             "Path": path, 
                                             "Name": name, 
                                             "Format": format,
                                             "Suffix": suffix,
                                             "Size": size,
                                             "ThumbnailPath": thumbnail_path,
                                             "Width": width,
                                             "Height": height,
                                             "CreatedBy": zfused_api.zFused.USER_ID,
                                             "CreatedTime": _current_time } )

    # _files = zfused_api.zFused.get("file", filter = { "MD5": md5} )
    if _status:
        return _value["Id"], "files create success"
    return False,"files create error"

def file_link(entity_type, entity_id, file_md5):
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    _files = zfused_api.zFused.get("file_link", filter = {"EntityType":entity_type, "EntityId":entity_id, "FileKey": file_md5} )
    if _files:
        return True, "file link is has"
    _value, _status = zfused_api.zFused.post( "file_link", data = { "EntityType":entity_type, 
                                                                    "EntityId":entity_id,
                                                                    "FileKey": file_md5,
                                                                    "CreatedBy": zfused_api.zFused.USER_ID,
                                                                    "CreatedTime": _current_time } )
    if _status:
        return _value["Id"], "file link create success"
    return False,"file link create error"

#zfused_api.zFused.post("file_link", data = {"EntityType":"report", "EntityId":_v, "FileKey": _file_md5})

# if __name__ == "__main__":
#     zfused_api.zFused("http://127.0.0.1:8080", "xiangda.liu", "12345678").login()
#     new_file("0376110c045edb5026b2cb8931e117a0","storage/video//2019/12/06/0376110c045edb5026b2cb8931e117a0.mp4", "tvc_an_v02_20191129.mp4", "MP4", ".mp4", 31420456) 