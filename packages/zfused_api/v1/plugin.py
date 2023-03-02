# coding:utf-8
# --author-- lanhua.zhou
from collections import defaultdict

import os
import time
import datetime
import shutil
import logging
import re

from . import _Entity
import zfused_api


logger = logging.getLogger(__name__)


def cache(project_id_list = []):
    """ init project assets
    """

    _s_t = time.time()
    if not project_id_list:
        _plugins = zfused_api.zFused.get("plugin")
    else:
        _project_ids = "|".join(map(str,project_id_list))
        _plugins = zfused_api.zFused.get("plugin", filter = {"ProjectId__in": _project_ids})
    if _plugins:
        list(map(lambda _plugin: Plugin.global_dict.setdefault(_plugin["Id"],_plugin), _plugins))
    _e_t = time.time()
    logger.info("plugin cache time = " + str(1000*(_e_t - _s_t)) + "ms")
    return _plugins


class Plugin(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Plugin, self).__init__("plugin", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("plugin", self._id)
                if not isinstance(_data, dict):
                    logger.error("plugin id {0} not exists".format(self._id))
                    self._data = {}
                    return None
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def full_name_code(self):
        return self.name_code()

    def color(self):
        return self._data.get("Color")

    def update_color(self, color):
        self.global_dict[self._id]["Color"] = color
        self._data["Color"] = color
        v = self.put("plugin", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

    def script(self):
        """get script 
        :rtype: str        
        """
        return self._data["Script"]

    def update_script(self, script):
        """ update check script
        :param script: 
        :rtype: bool
        """
        self.global_dict[self._id]["Script"] = script
        self._data["Script"] = script
        v = self.put("plugin", self._data["Id"], self._data)
        if v:
            return True
        else:
            return False

