# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import time
import datetime
import logging

from . import _Entity
import zfused_api
#from . import task

logger = logging.getLogger(__name__)


def new_process_node(name, code, color, description = ""):
    """ 创建新进度节点
    """
    _current_time = "%s+00:00"%datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _process_nodes = zfused_api.zFused.get( "process_node", 
                                            filter = {"code": code} )
    if _process_nodes:
        return "{} is exists".format(name), False
    _create_by = zfused_api.zFused.USER_ID
    _process_node, _status = zfused_api.zFused.post(key = "process_node", data = { "Name": name,
                                                                                   "Code": code,
                                                                                   "Color": color,
                                                                                   "Description":description,
                                                                                   "CreatedBy":_create_by,
                                                                                   "CreatedTime":_current_time })
    if _status:
        return _process_node["Id"], True
    return "{} create error".format(name), False

def cache(project_id = []):
    """ init project versions
    """
    process_node.global_dict = {}
    if not project_id:
        _process_nodes = zfused_api.zFused.get("process_node")
    else:
        _project_ids = "|".join([str(_project_id) for _project_id in project_id])
        _process_nodes = zfused_api.zFused.get("process_node", filter = {"ProjectId__in": _project_ids}, sortby = ["Id"], order = ["desc"])
    if _process_nodes:
        list(map(lambda _process_node: process_node.global_dict.setdefault(_process_node["Id"],_process_node), _process_nodes))
    return _process_nodes

def cache_from_ids(ids):
    _s_t = time.clock()
    ids = "|".join(map(str, ids))
    _process_nodes = zfused_api.zFused.get("process_node", filter = {"Id__in": ids})

    if _process_nodes:
        list(map(lambda _process_node: process_node.global_dict.setdefault(_process_node["Id"],_process_node), _process_nodes))
    _e_t = time.clock()
    return _process_nodes

class ProcessNode(zfused_api.zFused):
    global_dict = defaultdict(dict)
    def __init__(self, id, data = None):
        self._id = id
        self._data = data

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get("process_node", filter = {"Id":self._id})
                if not _data:
                    logger.error("process_node id {0} not exists".format(self._id))
                    return
                self._data = _data[0]
                self.global_dict[self._id] = _data[0]
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def object(self):
        return "process_node"

    def id(self):
        return self._id

    def data(self):
        return self._data

    def code(self):
        """
        get code

        rtype: str
        """
        return u"{}".format(self._data["Name"])

    def name(self):
        """
        get name

        rtype: str
        """
        return u"{}".format(self._data["Name"])

    def name_code(self):
        """
        get name code

        rtype: str
        """
        return u"{}({})".format(self.name(), self.code())

    def full_code(self):
        """
        get full path code

        rtype: str
        """
        return ""

    def full_name(self):
        """
        get full path name

        rtype: str
        """
        return u"{}".format(self._data["Name"])

    def full_name_code(self):
        """
        get full path name and code

        rtype: str
        """
        return u"{}({})".format(self.full_name(), self.full_code())

    def file_code(self):
        """ get file name

        :rtype: str
        """
        _link_handle = zfused_api.objects.Objects(self._data["Object"], self._data["LinkId"])
        return _link_handle.file_code()

    def description(self):
        return self._data["Description"]

    # def created_by(self):
    #     return self.global_dict[self._id]["CreatedBy"]

    # def created_time(self):
    #     """ get create time

    #     rtype: datetime.datetime
    #     """
    #     _time_text = self._data["CreatedTime"]
    #     if _time_text.startswith("0001"):
    #         return None
    #     _time_text = _time_text.split("+")[0].replace("T", " ")
    #     return datetime.datetime.strptime(_time_text, "%Y-%m-%d %H:%M:%S")