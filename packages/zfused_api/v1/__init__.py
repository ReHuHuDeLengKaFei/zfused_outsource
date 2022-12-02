# coding:utf-8
# --author-- lanhua.zhou

from __future__ import print_function
from functools import wraps

import os

import sys
import time
import datetime
import json
import hashlib
import copy
import logging
import re

import requests

httpsession = requests.session()
_cloud_session = requests.session()

__version__ = "v1"

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)

def reset( func ):
    @wraps(func)
    def wrap( *args, **kwargs ):
        zFused.RESET = True
        try:
            return func( *args, **kwargs )
        except Exception as e:
            logger.warning(e)
        finally:
            zFused.RESET = False
    return wrap
LOCAL_DATABASE_PATH =  os.path.abspath(os.path.join(os.path.dirname(__file__),"..", "..", "..", "database"))
LOCAL_KEY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", "..", ".."))
# print(LOCAL_DATABASE_PATH)

key_licence = ""

key_lic = "{}/key.lic".format(LOCAL_KEY_PATH)
if not os.path.isfile(key_lic):
    key_lic = "{}/key.lic".format(os.path.dirname(os.path.abspath(__file__)))
if not os.path.isfile(key_lic):
    key_lic = "C:/key.lic"

if os.path.isfile(key_lic):
    with open(key_lic, "r") as key_file:
        key_licence = key_file.read()



class zFused(object):
    RESET = False

    NAME = None
    KEY = None

    USER = None
    USER_ID = 0
    
    # company
    COMPANY_ID = 0

    HOST = "47.103.77.93"
    PORT = 8888
    
    INTERNAL_API_SERVER_ADDR = "http://47.103.77.93:8888"
    INTERNAL_API_SERVER_PATH = "{}/{}".format(INTERNAL_API_SERVER_ADDR, __version__)

    CLOUD_TRANS_SERVER_ADDR = "47.103.77.93:7005"
    INTERNAL_TRANS_SERVER_ADDR = "47.103.77.93:7005"

    CLOUD_IMAGE_SERVER_ADDR = "http://47.103.77.93:7006"
    INTERNAL_IMAGE_SERVER_ARRD = "http://47.103.77.93:7006"
    
    MQ_SERVER_ADDR = "47.103.77.93:5672"

    # cloud server
    CLOUD_SERVER_ADDR = "http://47.103.77.93:8888"
    CLOUD_SERVER_PATH = "{}/{}".format(CLOUD_SERVER_ADDR, __version__)

    def __init__(self, name, password ):

        zFused.NAME = name
        zFused.PASSWORD = password
        
    @classmethod
    def Login(cls, name, key):
        _zfused = zFused( name, key )
        _user_data = _zfused.get("user", filter = {"Username": name})
        if not _user_data:
            logger.error("{} is not exists".format(zFused.NAME))
            _company = _zfused.get("company", filter = {"Code": name})
            if _company:
                return True,""
            return False, "{} is not exists".format(zFused.NAME)
        _md = hashlib.md5()
        _md.update(zFused.PASSWORD.encode("utf-8"))
        if _user_data[0]["Password"] != _md.hexdigest():
            logger.error("password error")
            return False, "password error"
        zFused.USER_ID = _user_data[0]["Id"]
        zFused.COMPANY_ID = _zfused.get("user_profile", filter = {"UserId": zFused.USER_ID})[0]["CompanyId"]
        return True, ""

    @classmethod
    def get(cls, key, filter = {}, fields = [], sortby = [], order = [], offset = None, limit = 999999, active = True, distinct = False):
        """get data
        rtype: list
        """

        # local database
        _database_file = "{}/{}.json".format(LOCAL_DATABASE_PATH, key)
        if os.path.isfile(_database_file):
            with open(_database_file, "r") as handle:
                data = handle.read()
                jsdata = json.loads(data)
                return jsdata

        server = "%s/%s" % (zFused.INTERNAL_API_SERVER_PATH, key)
        # cloud server
        _cloud_server = "%s/%s" % (zFused.CLOUD_SERVER_PATH, key)
        params = {}
        if filter:
            params["query"] = ",".join(
                ["%s:%s" % (i, filter[i]) for i in filter.keys()])
        if fields:
            params["fields"] = ",".join(fields)
        if sortby:
            params["sortby"] = ",".join(sortby)
        if order:
            params["order"] = ",".join(order)
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        if distinct:
            params["distinct"] = distinct
        headers = { 'content-type': 'application/json', 
                    "key": key_licence }
        try:
            r = httpsession.get(server, params=params,
                             verify=True, headers=headers)
            if r.status_code == 200:
                return r.json() if r.json() else []
            else:
                return []
        except :
            logger.error("Timeout occurred")
            return []

    @classmethod
    def get_one(cls, key, id):
        """get data
        rtype: dict
        """
        _database_file = "{}/{}.json".format(LOCAL_DATABASE_PATH, key)
        if os.path.isfile(_database_file):
            with open(_database_file, "r") as handle:
                data = handle.read()
                jsdata = json.loads(data)
                for _data in jsdata:
                    if id == _data.get("Id"):
                        return _data
                return {}

        server = "{}/{}/{}".format(zFused.INTERNAL_API_SERVER_PATH, key, id)
        headers = { 'content-type': 'application/json', 
                    "key": key_licence }
        try:
            r = httpsession.get(server, verify=True, headers=headers)
            if r.status_code == 200:
                return r.json()
            else:
                return False
        except :
            logger.warning("Timeout occurred")
            return False
        return False

    @classmethod
    def post(cls, key, data):
        """get data
        rtype: bool
        """
        server = "%s/%s" % (zFused.INTERNAL_API_SERVER_PATH, key)
        data_json = json.dumps(data)
        r = httpsession.post(server, data = data_json)
        
        if r.status_code == 201:
            return eval(r.text), True
        else:
            return r.text, False
            
    @classmethod
    def put(cls, key, uid, data, change_field = "", send_message = True):
        server = "%s/%s/%s" % (zFused.INTERNAL_API_SERVER_PATH, key, uid)
        for _key, _item in data.items():
            try:
                # python3 has no unicode
                _is = False
                if sys.version.startswith("3"):
                    if isinstance(_item, str):
                        _is = True
                else:
                    if isinstance(_item, unicode): 
                        _is = True
                if _is:
                    if "+08:00" in _item:
                        data[_key] = _item.replace("+08:00", "+00:00")
            except:
                if isinstance(_item, str):
                    if "+08:00" in _item:
                        data[_key] = _item.replace("+08:00", "+00:00")

        new_data = copy.deepcopy(data)
        if "Id" in new_data.keys():
            new_data.pop("Id")

        data_json = json.dumps(new_data)
        r = httpsession.put(server, data = data_json)

        if r.status_code == 200:
            return True
        else:
            return False

    @classmethod
    def delete(cls, key, uid):
        server = "%s/%s/%s" % (zFused.INTERNAL_API_SERVER_PATH, key, uid)
        r = httpsession.delete(server)

        if r.status_code == 200:
            return True
        else:
            return False

    def xattr(self, attr_code):
        u""" 获得扩展属性值,没有返回默认值
        """
        _attr_datas = self.get('xattr', filter={'Code': attr_code})
        if not _attr_datas:
            return
        else:
            _attr_data = _attr_datas[0]
            _attr_links = self.get('xattr_link', filter={'LinkObject': self.object(), 'LinkId': self._id, 'XattrId': _attr_data['Id']})
            if not _attr_links:
                return _attr_data['DefaultValue']
            if _attr_data['Type'].startswith('@'):
                _object = _attr_data['Type'][1::]
                return [ zfused_api.objects.Objects(_object, int(_attr_link['Value'])) for _attr_link in _attr_links ]
            return [ _attr_link['Value'] for _attr_link in _attr_links ][0]

    def update_xattr(self, attr_code, value):
        """ 
        """
        _attr_datas = self.get('xattr', filter={'Code': attr_code})
        _attr_data = _attr_datas[0]
        _attr_links = self.get('xattr_link', filter={'LinkObject': self.object(), 'LinkId': self._id, 'XattrId': _attr_data['Id']})
        if not _attr_links:
            _data = {'XattrId': _attr_data['Id'], 'LinkObject': self.object(), 'LinkId': self._id, 'Value': value}
            self.post('xattr_link', _data)
        else:
            _data = _attr_links[0]
            _data['Value'] = value
            v = self.put('xattr_link', _data['Id'], _data)
            if v:
                return True
            return False

            

class _Entity(zFused):
    global_dict = {}
    def __init__(self, entity_type, entity_id, entity_data):
        self._type = entity_type
        self._id = entity_id
        self._data = entity_data

        self._extra_attrs = {}

    def _recheck(func):
        # def magic( self ) :
        #     print("start magic")
        #     if not isinstance(self._data, dict):
        #         self._data = self.get_one(self._type, self._id)
        #         self.global_dict[self._id] = self._data
        #     func( self )
        #     print("end magic")
        # return magic
        @wraps(func)
        def wrap( self, *args, **kwargs ):
            if not isinstance(self._data, dict):
                self._data = self.get_one(self._type, self._id)
                self.global_dict[self._id] = self._data
            return func( self, *args, **kwargs )
        return wrap

    def __eq__(self, other):
        return self._id == other._id and self._type == other._type

    def __key(self):
        return (self._type, self._id)

    def __hash__(self):
        return hash(self.__key())

    def id(self):
        return self._id

    def object(self):
        return self._type

    @_recheck
    def entity_type(self):
        return self._type

    @_recheck
    def entity_id(self):
        return self._id

    @_recheck
    def entity_data(self):
        return self._data
    
    @_recheck
    def data(self):
        return self._data
    
    @_recheck
    def code(self):
        return self._data.get("Code")

    @_recheck
    def name(self):
        return self._data.get("Name")

    @_recheck
    def name_code(self):
        return u"{}({})".format(self.name(), self.code())

    @_recheck
    def is_archive(self):
        return self._data.get("IsArchive")

    @_recheck
    def archive_id(self):
        return self._data.get("ArchiveId")

    def match(self, text):
        pass

    @_recheck
    def sort(self):
        if "Sort" in self._data:
            return self._data.get("Sort")
        else:
            return 0

    @_recheck
    def update_sort(self, value):
        if "Sort" not in self._data:
            return
        if self.global_dict[self._id]["Sort"] == value:
            return True
        self.global_dict[self._id]["Sort"] = value
        self._data["Sort"] = value
        v = self.put(self._type, self._id, self._data, "sort")
        if v:
            return True
        else:
            return False
    @_recheck
    def created_by(self):
        return self._data.get("CreatedBy")

    @_recheck
    def created_time(self):
        _time_text = self._data["CreatedTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")
    
    @_recheck
    def update_created_time(self):
        _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.global_dict[self._id]["CreatedTime"] = _current_time
        self._data["CreatedTime"] = _current_time
        v = self.put(self._type, self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    @_recheck
    def thumbnail_path(self):
        return self._data["ThumbnailPath"]

    def get_custom_path(self, custom_path):
        _re_com = re.compile(r"(\{.*?\})")
        _re_list = re.findall(_re_com, custom_path)
        if _re_list:
            for _re in _re_list:
                exec("global _re_value;_re_value = {}".format(_re.replace("{","").replace("}", "")))
                global _re_value
                custom_path = custom_path.replace(_re, _re_value)
        return custom_path

    def get_custom(self, custom):
        _re_com = re.compile(r"(\{.*?\})")
        _re_list = re.findall(_re_com, custom)
        if _re_list:
            for _re in _re_list:
                exec("global _re_value;_re_value = {}".format(_re.replace("{","").replace("}", "")))
                global _re_value
                custom = custom.replace(_re, _re_value)
        return custom

    def variables(self):
        pass
    
    def get_attr(self, name, type = "int"):
        _defualt = None
        if type == "float":
            _defualt = 0.0
        elif type == "int":
            _defualt = 0
        elif type == "str":
            _defualt = ""
        elif type == "list":
            _defualt = []
        elif type == "dict":
            _defualt = {}
        if not name in self._extra_attrs:
            self._extra_attrs[name] = _defualt
        return self._extra_attrs[name]
    
    def set_attr(self, name, value):
        self._extra_attrs[name] = value

    @_recheck
    def property(self, key = ""):
        _property =  self._data.get("Property")
        if not _property:
            return {}
        if key:
            return eval(_property).get(key)
        return eval(_property)

    @_recheck
    def update_property(self, key, value):
        _property = self.property()
        _property[key] = value
        self._data["Property"] = str(_property)
        v = self.put(self._type, self._id, self._data, "property", False)
        if v:
            return True
        else:
            return False

    @_recheck
    def update_name(self, name):
        self.global_dict[self._id]["Name"] = name
        self._data["Name"] = name
        v = self.put(self._type, self._data["Id"], self._data, "name")
        if v:
            return True
        else:
            return False

    @_recheck
    def update_code(self, code):
        self.global_dict[self._id]["Code"] = code
        self._data["Code"] = code
        v = self.put(self._type, self._data["Id"], self._data, "code")
        if v:
            return True
        else:
            return False

    # def add_note(self, title, rich_text = ""):
    #     _created_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    #     _created_by = zfused_api.zFused.USER_ID

    #     _status_id = zfused_api.status.active_status_ids()[0]

    #     _note, _status = zfused_api.zFused.post( key = "note", 
    #                                                     data = { "EntityType": self._type,
    #                                                              "EntityId": self._id,
    #                                                              "Title": title,
    #                                                              "RichText": rich_text,
    #                                                              "Status": 0,
    #                                                              "CreatedBy": _created_by,
    #                                                              "CreatedTime": _created_time } )
    #     if not _status:
    #         return u"{} create error".format(title), False

    #     _note_id = _note.get("Id")

    #     _user_ids = zfused_api.zFused.get("group_user", filter = {"EntityType": self._type,"EntityId": self._id})
    #     if _user_ids:
    #         _user_ids = [_group_user.get("UserId") for _group_user in _user_ids]
    #     else:
    #         _user_ids = [zfused_api.zFused.USER_ID]

    #     zfused_api.im.submit_message( "user",
    #                                   _created_by,
    #                                   _user_ids,
    #                                   { "entity_type": self._type,
    #                                     "entity_id": self._id },
    #                                   "note", 
    #                                   self._type,
    #                                   self._id,
    #                                   self._type,
    #                                   self._id )

    #     return _note_id, True

    @_recheck
    def note_count(self):
        return self._data.get("NoteCount")

    @_recheck
    def update_note_count(self, count):
        self.global_dict[self._id]["NoteCount"] = count
        self._data["NoteCount"] = count
        v = self.put(self._type, self._data["Id"], self._data, "note_count", False)
        if v:
            return True
        else:
            return False
        
    _recheck = staticmethod( _recheck )