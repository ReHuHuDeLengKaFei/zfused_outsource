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

logger = logging.getLogger(__name__)


class TaskPanelWidget(QtWidgets.QFrame):
    received = QtCore.Signal(str, int)
    published = QtCore.Signal(str, int, dict)
    def __init__(self, parent=None):
        super(TaskPanelWidget, self).__init__(parent)
        self._build()

        self._task_id = 0

        self.publish_button.clicked.connect(self._publish_new)

    def _publish_new(self):
        self.published.emit("new", self._task_id, {})

    def refresh(self):
        self.load_task_id(self._task_id)

    def load_task_id(self, task_id):
        logger.info("task panel load task id {}".format(task_id))
        self._task_id = task_id
        if not task_id:
            return
        _task = zfused_api.task.Task(task_id)
        self.path_lineedit.setText(_task.transfer_path())

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        _layout.addStretch(True)

        # =======================================================================
        # step by step widget
        self.step_widget = QtWidgets.QFrame()
        _layout.addWidget(self.step_widget)
        self.step_layout = QtWidgets.QVBoxLayout(self.step_widget)
        # step 1
        self.one_step_label = QtWidgets.QLabel()
        self.step_layout.addWidget(self.one_step_label)
        self.one_step_label.setText(u"第一步：确认上传雷区")
        # step 2
        self.two_step_label = QtWidgets.QLabel()
        self.step_layout.addWidget(self.two_step_label)
        self.two_step_label.setText(u"第二步：检查文件")
        # step 3
        self.three_step_label = QtWidgets.QLabel()
        self.step_layout.addWidget(self.three_step_label)
        self.three_step_label.setText(u"第三步：上传文件")

        # 
        _layout.addStretch(True)

        # path widget
        self.path_widget = QtWidgets.QFrame()
        _layout.addWidget(self.path_widget)
        self.path_layout = QtWidgets.QHBoxLayout(self.path_widget)
        self.path_label = QtWidgets.QLabel()
        self.path_layout.addWidget(self.path_label)
        self.path_label.setText(u"文件上传路径：")
        self.path_lineedit = QtWidgets.QLineEdit()
        self.path_layout.addWidget(self.path_lineedit)

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