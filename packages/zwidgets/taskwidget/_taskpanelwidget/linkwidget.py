# coding:utf-8
# --author-- lanhua.zhou

""" 任务面板 """

from __future__ import print_function

from functools import partial
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import button

__all__ = ["LinkWidget"]

class LinkWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(LinkWidget, self).__init__(parent)
        self._build()

    def load_task_id(self, task_id):
        """ load task id and get link object
        :rtype: None
        """
        _task_handle = zfused_api.task.Task(task_id)
        _link_handle = _task_handle.entity()
        self.link_button.setText(_link_handle.full_code())

    def _build(self):
        # build widget
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # link button
        self.link_button = QtWidgets.QPushButton()
        _layout.addWidget(self.link_button)
        self.link_button.setIcon(QtGui.QIcon(resource.get("icons", "view.png")))
        self.link_button.setObjectName("title_button")
        self.link_button.setFixedHeight(20)
        self.link_button.setFlat(True)

        # _layout.addStretch()