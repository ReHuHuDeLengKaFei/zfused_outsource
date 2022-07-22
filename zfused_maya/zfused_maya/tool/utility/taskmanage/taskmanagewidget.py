# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import maya.cmds as cmds

import zfused_api

import zfused_maya.core.record as record

from zwidgets.taskwidget import taskmanagewidget

from zfused_maya.ui.widgets import window
from zfused_maya.ui.widgets import checkwidget

import zfused_maya.node.inputattr.util as in_util
import zfused_maya.node.outputattr.util as out_util


__all__ = ["TaskManageWidget"]

logger = logging.getLogger(__name__)


class TaskManageWidget(window._Window):
    def __init__(self, parent = None):
        super(TaskManageWidget, self).__init__()
        self._build()

        self.task_widget.checked.connect(self._check)
        self.task_widget.quick_downloaded.connect(self._quick_download)
        self.task_widget.quick_published.connect(self._quick_publish)

        self.task_widget.task_panel_widget.received.connect(self._receive_file)
        self.task_widget.task_panel_widget.published.connect(self._publish_file)
        self.task_widget.task_panel_widget.opened.connect(self._open_file)

    def _check(self, task_id):
        """检查任务文件规范
        """
        _task = zfused_api.task.Task(task_id)
        _project_step = _task.project_step()
        _project_step_checks = _project_step.checks()
        if _project_step_checks:
            _ui = checkwidget.CheckWidget(_project_step_checks)
            _ui.show()

    def _quick_download(self, task_id):
        _task = zfused_api.task.Task(task_id)
        _last_version_id = _task.last_version_id()
        if _last_version_id:
            in_util.receive_version_file(_last_version_id)

    def _quick_publish(self, task_id):
        out_util.publish_file(task_id, {"description": u"快速发布"})

    def _open_file(self, file_path):
        cmds.file(file_path, o = True, f = True)    

    def _receive_file(self, mode, id, input_tasks = []):
        """ load sel index file
        :rtype: None
        """
        if mode == "version":
            in_util.receive_version_file(id)
        elif mode == "task":
            in_util.assembly_file(id, input_tasks)
        elif mode == "update":
            in_util.update_file(id, input_tasks)
            
    def _publish_file(self, task_id, info, extend_attr = {}):
        _task = zfused_api.task.Task(task_id)
        # check shot frame
        _project_entity = _task.project_entity()
        if isinstance(_project_entity, zfused_api.shot.Shot):
            # get start frame and end frame
            min_frame = cmds.playbackOptions(q = True, min = True)
            max_frame = cmds.playbackOptions(q = True, max = True)
            if int(min_frame) != int(_project_entity.data().get("FrameStart")) or int(max_frame) != int(_project_entity.data().get("FrameEnd")):
                cmds.confirmDialog(message=u"帧数设置不对")
                return False

        _value = False
        attrs = extend_attr.get("attrs")
        elements = extend_attr.get("elements")
        if attrs or elements:
            _value = out_util.fix_file(task_id, info, extend_attr)
        else:
            _value = out_util.publish_file(task_id, info, extend_attr)

        # if mode == "new":
        #     _value = out_util.publish_file(task_id, info, elements)
        # elif mode == "fix":
        #     _value = out_util.fix_file(task_id, info)
            
        if _value:
            self.load_task_id(task_id)

    def _build(self):
        self.resize(1600, 900)
        self.set_title_name(u"任务管理(task management)")

        self.task_widget = taskmanagewidget.TaskManageWidget()
        self.set_central_widget(self.task_widget)

    def showEvent(self, event):
        _project_id = record.current_project_id()
        _company_id = record.current_company_id()
        self.task_widget.load(_project_id, _company_id)
        super(TaskManageWidget, self).showEvent(event)