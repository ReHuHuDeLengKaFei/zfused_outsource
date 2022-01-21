# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

from . import _Entity
import zfused_api

logger = logging.getLogger(__name__)


# def cache():
#     _softwares = zfused_api.zFused.get("Software", sortby = ["Code","Version"], order=["asc"])
#     if _softwares:
#         return [Software(_software)]



class Software(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(Software, self).__init__("software", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("software", self._id)
                if not _data:
                    logger.error("software id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def code(self):
        """ get software code
        rtype: str
        """
        return u"{}{}".format(self._data["Code"], self._data["Version"])

    # def name(self):
    #     """ get software name
    #     rtype: str
    #     """
    #     return u"{}{}".format(self._data["Name"], self._data["Version"])

    def version(self):
        return self._data.get("Version")

    def file_path(self):
        return self.code()

    def init_script(self):
        return self._data.get("InitScript")

    def update_init_script(self, init_script):
        if self._data.get("InitScript") == init_script:
            return True
        self.global_dict[self._id]["InitScript"] = init_script
        self._data["InitScript"] = init_script
        v = self.put("software", self._id, self._data, "init_script")
        if v:
            return True
        else:
            return False

    def python_init_script(self):
        return self._data.get("PythonInitScript")

    def update_python_init_script(self, init_script):
        if self._data.get("PythonInitScript") == init_script:
            return True
        self.global_dict[self._id]["PythonInitScript"] = init_script
        self._data["PythonInitScript"] = init_script
        v = self.put("software", self._id, self._data, "python_init_script")
        if v:
            return True
        else:
            return False

    def executable_path(self):
        """可执行文件
        rtype: str
        """
        _paths = self._data.get("ExecutablePath").split(";")
        if _paths:
            for _path in _paths:
                if os.path.isfile(_path):
                    return _path
        return None

        # return self._data.get("ExecutablePath")
        # _paths = self._data.get("ExecutablePath").split(";")
        # if _paths:
        #     for _path in _paths:
        #         if os.path.isfile(_path):
        #             return _path
        # return None

    def executable_python_path(self):
        """可执行python文件
        rtype: str
        """
        _paths = self._data.get("ExecutablePythonPath").split(";")
        if _paths:
            for _path in _paths:
                if os.path.isfile(_path):
                    return _path
        return None


class ProjectSoftware(_Entity):
    global_dict = {}
    def __init__(self, entity_id, entity_data = None):
        super(ProjectSoftware, self).__init__("project_software", entity_id, entity_data)

        if not self.global_dict.__contains__(self._id) or zfused_api.zFused.RESET:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                _data = self.get_one("project_software", self._id)
                if not _data:
                    logger.error("project software id {0} not exists".format(self._id))
                    return
                self._data = _data
                self.global_dict[self._id] = _data
        else:
            if self._data:
                self.global_dict[self._id] = self._data
            else:
                self._data = self.global_dict[self._id]

    def startup_script(self):
        return self._data.get("StartupScript")

    def update_startup_script(self, startup_script):
        if self._data.get("StartupScript") == startup_script:
            return True
        self.global_dict[self._id]["StartupScript"] = startup_script
        self._data["StartupScript"] = startup_script
        v = self.put("project_software", self._id, self._data, "startup_script")
        if v:
            return True
        else:
            return False

    def software(self):
        return zfused_api.software.Software(self._data.get("SoftwareId"))

    def project(self):
        return zfused_api.project.Project(self._data.get("ProjectId"))

    def project_id(self):
        return self._data.get("ProjectId")