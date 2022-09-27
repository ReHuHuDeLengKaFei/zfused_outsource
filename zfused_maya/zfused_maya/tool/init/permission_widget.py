# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import maya.cmds as cmds

import zfused_api

import zfused_maya.core.record as record

from zwidgets.permission_widget import project_widget

from zfused_maya.ui.widgets import window

logger = logging.getLogger(__name__)


class PermissionWidget(window._Window):
    def __init__(self, parent = None):
        super(PermissionWidget, self).__init__()
        self._build()

    def _build(self):
        self.resize(800, 400)
        self.set_title_name(u"文件夹权限检查")

        self.permission_widget = project_widget.ProjectWidget()
        self.set_central_widget(self.permission_widget)

    def showEvent(self, event):
        super(PermissionWidget, self).showEvent(event)
        _project_id = record.current_project_id()
        self.permission_widget.load_project_id(_project_id)
        self.permission_widget.check()