# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)

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


class File(_Entity):

    @classmethod
    def new(cls, name, user_ids, mode = 0):
        """
        0 single chat
        1 group chat
        """
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID

        user_ids.sort()
        _code = "|".join([str(_user_id) for _user_id in user_ids])
        _is_has = zfused_api.zFused.get("group", filter = {"Code": _code, "Mode": mode})
        if _is_has:
            return _is_has[0].get("Id"), True

        _group, _status = zfused_api.zFused.post( key = "group", 
                                                  data = { "Name": name,
                                                           "Code": _code,
                                                           "Mode": mode,
                                                           "CreatedBy": _created_by,
                                                           "CreatedTime": _created_time } )
        if not _status:
            return u"{} create error".format(name), False

        _group_id = _group.get("Id")

        # group user
        for _user_id in user_ids:
            zfused_api.zFused.post( "group_user", { "EntityType": "group", 
                                                    "EntityId": _group_id, 
                                                    "UserId": _user_id,
                                                    "CreatedBy": _created_by,
                                                    "CreatedTime": _created_time })
        return _group_id, True

    
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(File, self).__init__("file", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("file", self._id)
                if not isinstance(_data, dict):
                    logger.error("file id {0} not exists".format(self._id))
                    self._data = {}
                    return None
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]
                
        if self._id not in self.global_dict:
            self.global_dict[self._id] = self._data


    @_Entity._recheck
    def get_thumbnail(self):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None