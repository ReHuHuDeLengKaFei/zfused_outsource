# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import maya.cmds as cmds

import zfused_api

import zfused_maya.core.record as record

from zwidgets.task_receive_widget import task_receive_widget

from zfused_maya.ui.widgets import window

logger = logging.getLogger(__name__)


class TaskReceiveManageWidget(window._Window):
    def __init__(self, parent = None):
        super(TaskReceiveManageWidget, self).__init__()
        self._build()

    def _build(self):
        self.resize(1600, 900)
        self.set_title_name(u"任务接收管理(task receive management)")

        self.task_widget = task_receive_widget.TaskReceiveWidget()
        self.set_central_widget(self.task_widget)

    def showEvent(self, event):
        _project_id = record.current_project_id()
        _company_id = record.current_company_id()
        self.task_widget.load(_company_id, _project_id)
        super(TaskReceiveManageWidget, self).showEvent(event)