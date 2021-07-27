# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import time
import logging
import datetime

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


def new_library(name, code, path, color = None):
    _librarys = zfused_api.zFused.get( "library", filter = {"Code": code})
    if _librarys:
        return "{} is exists".format(name), False
    if not color:
        color = "#007acc"
    _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _created_by = zfused_api.zFused.USER_ID
    _library, _status = zfused_api.zFused.post(key = "library", data = { "Name": name,
                                                                         "Code": code,
                                                                         "Path": path,
                                                                         "Color": color,
                                                                         "CreatedBy":_created_by,
                                                                         "CreatedTime":_created_time })
    if _status:
        return _library["Id"], True
    return "{} create error".format(name), False

def new_entity(name, code, library_id, category_id, description = ""):
    _librarys = zfused_api.zFused.get( "library_entity", filter = {"Code": code, "LibraryId": library_id})
    if _librarys:
        return "{} is exists".format(name), False
    _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _created_by = zfused_api.zFused.USER_ID
    _entity, _status = zfused_api.zFused.post(key = "library_entity", data = { "Name": name,
                                                                               "Code": code,
                                                                               "LibraryId": library_id,
                                                                               "CategoryId": category_id,
                                                                               "Description": description,
                                                                               "CreatedBy":_created_by,
                                                                               "CreatedTime":_created_time })
    if _status:
        return _entity["Id"], True
    return "{} create error".format(name), False

def new_edition(library_id, library_entity_id, code, software_id, renderer, description, format, suffix, size):
    _librarys = zfused_api.zFused.get( "library_entity_edition", filter = {"Code": code, "library_entity_id": library_entity_id})
    if _librarys:
        # return "{} is exists".format(code), False
        zfused_api.zFused.delete("library_entity_edition", _librarys[0]["Id"])
    _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _created_by = zfused_api.zFused.USER_ID
    _edition, _status = zfused_api.zFused.post(key = "library_entity_edition", data = { "LibraryId": library_id,
                                                                                        "LibraryEntityId": library_entity_id,
                                                                                        "Code": code,
                                                                                        "SoftwareId": software_id,
                                                                                        "Renderer": renderer,
                                                                                        "Description": description,
                                                                                        "Format": format,
                                                                                        "Suffix": suffix,
                                                                                        "Size": size,
                                                                                        "ThumbnailPath":"",
                                                                                        "CreatedBy": _created_by,
                                                                                        "CreatedTime": _created_time })
    if _status:
        return _edition["Id"], True
    return "{} create error".format(code), False

def new(name, code, entity_type, category_id, description):
    _librarys = zfused_api.zFused.get( "library", filter = {"Code": code})
    if _librarys:
        return "{} is exists".format(name), False
    _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _created_by = zfused_api.zFused.USER_ID
    _library, _status = zfused_api.zFused.post(key = "library", data = { "Name": name,
                                                                         "Code": code,
                                                                         "EntityType": entity_type,
                                                                         "CategoryId": category_id,
                                                                         "Description":description,
                                                                         "CreatedBy":_created_by,
                                                                         "CreatedTime":_created_time })
    if _status:
        return Library(_library["Id"], _library), True
    return "{} create error".format(name), False

def clear(lis):
    del lis[:]

def cache():
    """ init library
    """
    _s_t = time.clock()
    _librarys = zfused_api.zFused.get("library")
    if _librarys:
        list(map(lambda _library: Library.global_dict.setdefault(_library["Id"], _library), _librarys))
        list(map(lambda _library: clear(Library.global_tags[_library["Id"]]) if Library.global_tags[_library["Id"]] else False, _librarys))
    # cache tags
    #_str_library_ids = [str(_library_id) for _library_id in Library.global_dict]
    #_tag_links = zfused_api.zFused.get("tag_link", filter = {"LinkObject": "library", "LinkId__in": "|".join(_str_library_ids)})
    # if _tag_links:
    #     for _tag_link in  _tag_links:
    #         _library_id = _tag_link["LinkId"]
    #         Library.global_tags[_library_id].append(_tag_link["TagId"])
    _e_t = time.clock()
    logger.info("library cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _librarys if _librarys else []

def entity_cache(library_id_list = []):
    _s_t = time.clock()
    _library_entitys = zfused_api.zFused.get("library_entity", sortby = ["code"], order = ["asc"])

    if not library_id_list:
        _library_entitys = zfused_api.zFused.get("library_entity", sortby = ["code"], order = ["asc"])
    else:
        _library_ids = "|".join(map(str, library_id_list))
        _library_entitys = zfused_api.zFused.get("library_entity", filter = {"LibraryId__in": _library_ids}, sortby = ["code"], order = ["asc"])

    if _library_entitys:
        list(map(lambda _library: LibraryEntity.global_dict.setdefault(_library["Id"], _library), _library_entitys))
        list(map(lambda _library: clear(LibraryEntity.global_tags[_library["Id"]]) if LibraryEntity.global_tags[_library["Id"]] else False, _library_entitys))
    
    # cache tags
    _str_library_ids = [str(_library_id) for _library_id in LibraryEntity.global_dict]
    _tag_links = zfused_api.zFused.get("tag_link", filter = {"LinkObject": "library_entity", "LinkId__in": "|".join(_str_library_ids)})
    if _tag_links:
        for _tag_link in  _tag_links:
            _library_id = _tag_link["LinkId"]
            LibraryEntity.global_tags[_library_id].append(_tag_link["TagId"])
    _e_t = time.clock()
    logger.info("library entity cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _library_entitys

        
class Library(_Entity):
    global_dict = {}
    global_tags = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(Library, self).__init__("library", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("library", self._id)
                if not _data:
                    logger.error("library id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def tag_ids(self):
        """ get library tag ids
        """
        if self._id not in self.global_tags or self.RESET:
            _tag_links = self.get("tag_link", filter = {"LinkObject": "library", "LinkId": self._id})
            if _tag_links:
                self.global_tags[self._id] = [_tag_link["TagId"] for _tag_link in _tag_links]
        return self.global_tags[self._id]

    def get_thumbnail(self, is_version = False):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

    def update_thumbnail_path(self, thumbnail_path):
        if self.global_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.global_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._data["ThumbnailPath"] = thumbnail_path
        v = self.put("library", self._data["Id"], self._data, "thumbnail_path")
        if v:
            return True
        else:
            return False

    def color(self):
        return self._data.get("Color")

    def set_category(self, category_id):
        if zfused_api.zFused.get("library_category", filter = {"LibraryId": self._id, "CategoryId": category_id}):
            return category_id, True
        _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        _created_by = zfused_api.zFused.USER_ID
        _links, _status = zfused_api.zFused.post( key = "library_category", 
                                                  data = { "LibraryId": self._id,
                                                            "CategoryId": category_id,
                                                            "CreatedBy":_created_by,
                                                            "CreatedTime":_created_time })
        if _status:
            return category_id, True
        return 0,False

    def new_category(self, name, code, color, description = ""):
        _category_id = 0
        _categorys = zfused_api.zFused.get( "category", filter = {"Code": code, "EntityType": "library"})
        if _categorys:
            _category_id = _categorys[-1]["Id"]
            if zfused_api.zFused.get("library_category", filter = {"LibraryId": self._id, "CategoryId": _category_id}):
                return _category_id, False
        else:
            _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            _created_by = zfused_api.zFused.USER_ID
            _category, _status = zfused_api.zFused.post(key = "category", data = { "Name": name,
                                                                                   "Code": code,
                                                                                   "EntityType": "library",
                                                                                   "color": color,
                                                                                   "Description":description,
                                                                                   "CreatedBy":_created_by,
                                                                                   "CreatedTime":_created_time })
            if _status:
                _category_id = _category["Id"]
        if _category_id:
            return self.set_category(_category_id)
        return 0, False

class LibraryEntity(_Entity):
    global_dict = {}
    global_tags = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(LibraryEntity, self).__init__("library_entity", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("library_entity", self._id)
                if not _data:
                    logger.error("library entity id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def get_thumbnail(self, is_version = False):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

    def update_thumbnail_path(self, thumbnail_path):
        if self.global_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.global_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._data["ThumbnailPath"] = thumbnail_path
        v = self.put("library_entity", self._data["Id"], self._data, "thumbnail_path")
        if v:
            return True
        else:
            return False

    def update_category(self, category_id):
        if self.global_dict[self._id]["CategoryId"] == category_id:
            return True
        self.global_dict[self._id]["CategoryId"] = category_id
        self._data["CategoryId"] = category_id
        v = self.put("library_entity", self._data["Id"], self._data, "category_id")
        if v:
            return True
        else:
            return False

    def tag_ids(self):
        """ get link tag ids
        """
        if self._id not in self.global_tags or self.RESET:
            _tag_links = self.get("tag_link", filter = {"LinkObject": "library_entity", "LinkId": self._id})
            if _tag_links:
                self.global_tags[self._id] = [_tag_link["TagId"] for _tag_link in _tag_links]
        return self.global_tags[self._id]

    def update_count(self):
        _editions = self.get("library_entity_edition", filter = {"LibraryEntityId": self._id})
        _count = self.data().get("Count")
        if len(_editions) == _count:
            return True
        _count = len(_editions)
        # _count += 1
        self.global_dict[self._id]["Count"] = _count
        self._data["Count"] = _count
        v = self.put("library_entity", self._data["Id"], self._data, "count")
        if v:
            return True
        else:
            return False


class LibraryEntityEdition(_Entity):
    global_dict = {}
    global_tags = defaultdict(list)
    def __init__(self, entity_id, entity_data = None):
        super(LibraryEntityEdition, self).__init__("library_entity_edition", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("library_entity_edition", self._id)
                if not _data:
                    logger.error("library entity edition id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def get_thumbnail(self, is_version = False):
        _thumbnail_path = self._data.get("ThumbnailPath")
        if _thumbnail_path:
            if _thumbnail_path.startswith("storage"):
                return "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _thumbnail_path.split("storage/")[-1])
        return None

    def update_thumbnail_path(self, thumbnail_path):
        if self.global_dict[self._id]["ThumbnailPath"] == thumbnail_path:
            return True
        self.global_dict[self._id]["ThumbnailPath"] = thumbnail_path
        self._data["ThumbnailPath"] = thumbnail_path
        v = self.put("library_entity_edition", self._data["Id"], self._data, "thumbnail_path")
        if v:
            return True
        else:
            return False