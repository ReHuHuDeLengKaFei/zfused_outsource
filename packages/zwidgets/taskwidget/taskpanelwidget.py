# coding:utf-8
# --author-- lanhua.zhou

""" 任务面板 """

from __future__ import print_function

from functools import partial
import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import button

logger = logging.getLogger(__file__)


class TaskPanelWidget(QtWidgets.QFrame):
    received = QtCore.Signal(str, int)
    published = QtCore.Signal(str, int, dict)
    def __init__(self, parent=None):
        super(TaskPanelWidget, self).__init__(parent)
        self._build()

        self._task_id = 0

    def refresh(self):
        self.load_task_id(self._task_id)

    def load_task_id(self, task_id):
        logger.info("task panel load task id {}".format(task_id))
        self._task_id = task_id
        if not task_id:
            return
        _task = zfused_api.task.Task(task_id)


    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # =======================================================================
        # step by step widget
        self.step_widget = QtWidgets.QFrame()
        _layout.addWidget(self.step_widget)
        self.step_layout = QtWidgets.QVBoxLayout(self.step_widget)
        # 

        # operation widget
        self.operation_widget = QtWidgets.QFrame()
        _layout.addWidget(self.operation_widget)
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_widget)
        self.publish_label = QtWidgets.QLabel()
        self.operation_layout.addWidget(self.publish_label)
        self.publish_label.hide()
        self.operation_layout.addStretch(True)
        self.publish_button = QtWidgets.QPushButton()
        self.operation_layout.addWidget(self.publish_button)
        self.publish_button.setObjectName("create_button")
        self.publish_button.setText(u"发布提交文件")
        self.publish_button.setFixedSize(100,40)