# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import wraps

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

HAS_HISTORY_TABLE = ["asset", "assembly", "shot", "sequence", "task", "episode"]

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

logger = logging.getLogger(__file__)

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


class zFused(object):
    RESET = False

    NAME = None
    KEY = None

    USER = None
    USER_ID = 0
    
    # 公司
    COMPANY_ID = 0
    
    INTERNAL_SERVER_ADDR = None
    INTERNAL_SERVER_PATH = None

    CLOUD_TRANS_SERVER_ADDR = None
    INTERNAL_TRANS_SERVER_ARRD = None

    CLOUD_IMAGE_SERVER_ADDR = None
    INTERNAL_IMAGE_SERVER_ARRD = None
    
    MQ_SERVER_ADDR = None

    # 新配置云空间
    CLOUD_SERVER_ADDR = "http://47.103.77.93:80"
    CLOUD_SERVER_PATH = "{}/{}".format(CLOUD_SERVER_ADDR, __version__)

    def __init__(self, name, password ):

        
        zFused.NAME = name
        zFused.PASSWORD = password
        
        # zFused.INTERNAL_SERVER_PATH = "{}/{}".format(api_server_addr, __version__)
        # zFused.CLOUD_TRANS_SERVER_ADDR = cloud_trans_server_addr if cloud_trans_server_addr else "{}:7005".format(_host)
        # zFused.INTERNAL_TRANS_SERVER_ADDR = internal_trans_server_addr if internal_trans_server_addr else "{}:7005".format(_host)
        # zFused.CLOUD_IMAGE_SERVER_ADDR = cloud_image_server_addr if cloud_image_server_addr else "http://{}:7006".format(_host)
        # zFused.INTERNAL_IMAGE_SERVER_ADDR = internal_image_server_addr if internal_image_server_addr else "http://{}:7006".format(_host)
        # zFused.MQ_SERVER_ADDR = mq_server_addr if mq_server_addr else "{}:5672".format(_host)

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
        server = "%s/%s" % (zFused.INTERNAL_SERVER_PATH, key)
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
        headers = {'content-type': 'application/json'}
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
        server = "{}/{}/{}".format(zFused.INTERNAL_SERVER_PATH, key, id)
        headers = {'content-type': 'application/json'}
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
        server = "%s/%s" % (zFused.INTERNAL_SERVER_PATH, key)
        data_json = json.dumps(data)
        r = httpsession.post(server, data = data_json)

        # cloud
        _cloud_server = "%s/%s" % (zFused.CLOUD_SERVER_PATH, key)
        try:
            _cloud_session.post(_cloud_server, data = data_json)
        except:
            pass
        
        try:
            if r.status_code == 201:
                if key not in HAS_HISTORY_TABLE:
                    return eval(r.text), True
                last_id = zFused.get(key)[-1]["Id"]
                try:
                    import zfused_api
                    zfused_api.im.submit_message( "user",
                                                  cls.USER_ID,
                                                  [],
                                                  { "msgtype": "new", 
                                                    "new": {"object": key, "object_id": last_id} }, 
                                                  "new",
                                                  key,
                                                  last_id )
                except Exception as e:  
                    logger.warning(e)

                currentTime = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                data_history = copy.deepcopy(data)
                data_history["ChangeBy"] = zFused.USER_ID
                data_history["ChangeTime"] = currentTime
                data_history["{}Id".format(key.capitalize())] = last_id
                _r = httpsession.post("{}_history".format(server), data = json.dumps(data_history))
                if _r.status_code == 201:
                    return eval(r.text), True
                else:
                    return r.text, False
            else:
                return r.text, False
        except Exception as e:
            logger.error(e)
            return r.text, False
            
    @classmethod
    def put(cls, key, uid, data, change_field = "", send_message = True):
        server = "%s/%s/%s" % (zFused.INTERNAL_SERVER_PATH, key, uid)
        # 更改数据时间 误差8小时机制
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

        # cloud
        _cloud_server = "%s/%s/%s" % (zFused.CLOUD_SERVER_PATH, key, uid)
        try:
            _cloud_session.put(_cloud_server, data = data_json)
        except:
            pass

        if r.status_code == 200:
            if key in HAS_HISTORY_TABLE and change_field != "":
                currentTime = "%s+00:00" % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                _field = u"%sId" % key.capitalize()
                data_history = copy.deepcopy(new_data)
                data_history[u"%sId" % key.capitalize()] = uid
                data_history[u"ChangeField"] = change_field
                data_history[u"ChangeBy"] = cls.USER_ID
                data_history[u"ChangeTime"] = currentTime
                # data_history_json = json.dumps(data_history)
                # r = httpsession.post( "%s/%s_history" %(zFused.INTERNAL_SERVER_PATH, key), data = data_history_json)
                _history, _status = cls.post("{}_history".format(key), data_history)
                # return _status
                if _status:
                    _last_id = _history["Id"]
                    try:
                        if send_message:
                            import zfused_api
                            zfused_api.im.submit_message( "user",
                                                        cls.USER_ID,
                                                        [],
                                                        { "msgtype": "update", 
                                                        "update": {"object": key, "object_id": uid, "object_history_id": _last_id} }, 
                                                        "update",
                                                        key,
                                                        uid )
                    except Exception as e:  
                        logger.warning(e)
            else:
                try:
                    if send_message:
                        import zfused_api
                        zfused_api.im.submit_message( "user",
                                                    cls.USER_ID,
                                                    [],
                                                    { "msgtype": "update",
                                                        "update": {"object": key, "object_id": uid} },
                                                        "update",
                                                    key,
                                                    uid )
                except Exception as e:  
                    logger.warning(e)
            return True
        else:
            return False

    @classmethod
    def delete(cls, key, uid):
        server = "%s/%s/%s" % (zFused.INTERNAL_SERVER_PATH, key, uid)
        r = httpsession.delete(server)

        # cloud
        _cloud_server = "%s/%s/%s" % (zFused.CLOUD_SERVER_PATH, key, uid)
        try:
            _cloud_session.delete(_cloud_server)
        except:
            pass

        if r.status_code == 200:
            # delete history
            if key not in HAS_HISTORY_TABLE:
                return True
            # get history id
            _historys = zFused.get("{}_history".format(key), filter = {"%sId" % key.capitalize() : uid})

            if _historys:
                for _history in _historys:
                    r = httpsession.delete("{}/{}_history/{}".format(zFused.INTERNAL_SERVER_PATH, key, _history["Id"]))
            return True
        else:
            return False


class _Entity(zFused):
    def __init__(self, entity_type, entity_id, entity_data):
        self._type = entity_type
        self._id = entity_id
        self._data = entity_data

        self._extra_attrs = {}

    def id(self):
        return self._id

    def object(self):
        return self._type

    def entity_type(self):
        return self._type

    def entity_id(self):
        return self._id

    def entity_data(self):
        return self._data

    def data(self):
        return self._data

    def code(self):
        """
        get code if has
 
        rtype: str
        """
        return self._data.get("Code")

    def name(self):
        """
        get name

        rtype: str
        """
        return self._data.get("Name")

    def name_code(self):
        """
        get name code

        rtype: str
        """
        return u"{}({})".format(self.name(), self.code())

    def created_by(self):
        return self._data["CreatedBy"]

    def created_time(self):
        """ get created time
        rtype: datetime.datetime
        """
        _time_text = self._data["CreatedTime"]
        if _time_text.startswith("0001"):
            return None
        _time_text = _time_text.split("+")[0].replace("T", " ")
        return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")

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

    def property(self, key = ""):
        _property =  self._data.get("Property")
        if not _property:
            return {}
        if key:
            return eval(_property.get(key))
        return eval(_property)

    def update_property(self, key, value):
        _property = self.property()
        _property[key] = value
        self._data["Property"] = str(_property)
        v = self.put(self._type, self._id, self._data, "property")
        if v:
            return True
        else:
            return False