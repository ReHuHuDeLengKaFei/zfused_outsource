# coding:utf-8
# --author-- lanhua.zhou

import subprocess
import logging

import zfused_api

logger = logging.getLogger("zcore.app")

__all__ = ["App"]

global global_startup_project_id,global_startup_task_id


class App(object):
    def __init__(self, software_id):
        self._software_id = software_id
        self._software = zfused_api.software.Software(software_id)

    def startup(self, mode = "executable", project_id = 0, task_id = 0):
        """
        """
        global_startup_project_id = project_id
        global_startup_task_id = task_id

        # 设置项目启动环境变量
        _project_softwares = zfused_api.zFused.get("project_software", filter = {"ProjectId": project_id, "SoftwareId": self._software_id})
        if _project_softwares:
            _project_software = _project_softwares[0]
            exec(_project_software.get("StartupScript"), globals())

        # 初始化 software script
        _init_script = self._software.init_script()
        exec(_init_script, globals())

        if mode == "executable":
            # 运行程序
            _executable_path = self._software.executable_path()
            _process = subprocess.Popen( _executable_path)
            print(_process.pid)
        elif mode == "executable_python":
            # 运行程序
            _executable_path = self._software.executable_python_path()
            _process = subprocess.Popen( _executable_path)
            print(_process.pid)