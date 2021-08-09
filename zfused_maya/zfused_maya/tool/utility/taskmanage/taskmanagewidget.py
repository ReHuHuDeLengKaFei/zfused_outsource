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

from zfused_maya.node.attribute import publishfile
from zfused_maya.node.attribute import receivefile

__all__ = ["TaskManageWidget"]

logger = logging.getLogger(__name__)


class TaskManageWidget(window._Window):
    def __init__(self, parent = None):
        super(TaskManageWidget, self).__init__()
        self._build()

        # self.task_widget.task_panel_widget.received.connect(self._receive_file)
        
        self.task_widget.task_panel_widget.published.connect(self._publish_file)
        self.task_widget.task_listwidget.published.connect(self._publish_file)

    def _build(self):
        self.resize(1600, 900)
        self.set_title_name(u"任务管理(task management)")

        self.task_widget = taskmanagewidget.TaskManageWidget()
        self.set_central_widget(self.task_widget)

    # def _receive_file(self, mode, id):
    #     """ load sel index file
    #     :rtype: None
    #     """
    #     if mode == "version":
    #         receivefile.receive_version_file(id)
    #     elif mode == "task":
    #         receivefile.assembly_file(id)

    def _publish_file(self, mode, task_id, info):
        _task = zfused_api.task.Task(task_id)
        _project_entity = _task.project_entity()

        _value = False
        if mode == "new":
            _value = publishfile.publish_file(task_id, info)
        elif mode == "fix":
            _value = publishfile.fix_file(task_id, info)
        if _value:
            self.load_task_id(task_id)

    def showEvent(self, event):
        _project_id = record.current_project_id()
        self.task_widget.load_project_id(_project_id)
        super(TaskManageWidget, self).showEvent(event)