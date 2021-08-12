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

from . import operationwidget
from . import linkwidget

logger = logging.getLogger(__file__)

class TaskPanelWidget(QtWidgets.QFrame):
    received = QtCore.Signal(str, int)
    published = QtCore.Signal(str, int, dict)
    def __init__(self, parent=None):
        super(TaskPanelWidget, self).__init__(parent)
        self._build()

        self._task_id = 0
        self._task_handle = None

        self.operation_widget.received.connect(self.received.emit)
        self.operation_widget.published.connect(self.published.emit)

    def refresh(self):
        self.load_task_id(self._task_id)

    def load_task_id(self, task_id):
        logger.info("task panel load task id {}".format(task_id))
        self._task_id = task_id
        if not task_id:
            return
        self._task_handle = zfused_api.task.Task(task_id)
        self._object_handle = zfused_api.objects.Objects(self._task_handle.data()["Object"], 
                                                         self._task_handle.data()["LinkId"])
        self.name_button.setText(self._task_handle.name())
        _thumbnail = self._object_handle.get_thumbnail()
        if not _thumbnail:
            _thumbnail = self._task_handle.get_thumbnail()
        if _thumbnail:
            self.thumbnail_button.set_thumbnail(_thumbnail)
        self.link_widget.load_task_id(task_id)
        self.operation_widget.load_task_id(task_id)

        # if self._task_handle.data().get("ProphetValue") == -1:
        #     self.lock_label.showNormal()
        #     self.lock_label.setText(u" 此任务由《先知系统》锁定，须由《先知系统》锁定人解锁！")
        #     self.operation_widget.set_locked(False)
        # elif self._task_handle.is_locked():
        #     self.lock_label.showNormal()
        #     _user_handle = zfused_api.user.User(self._task_handle.data().get("LockedBy"))
        #     self.lock_label.setText(u" 此任务被 {} 锁定，须由锁定人 {} 解锁！".format( _user_handle.name_code(), _user_handle.name_code() ))
        #     self.operation_widget.set_locked(False)
        # else:
        #     self.lock_label.hide()
        #     self.operation_widget.set_locked(True)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # self.lock_label = QtWidgets.QLabel()
        # self.lock_label.setFixedHeight(20)
        # self.lock_label.setStyleSheet("QLabel{background-color:rgba(253, 174, 23);color:#000000}")
        # self.lock_label.setText(u" 此任务由《先知系统》锁定，须由《先知系统》锁定人解锁！")
        # _layout.addWidget(self.lock_label)

        # entity widget
        self.link_widget = linkwidget.LinkWidget()
        _layout.addWidget(self.link_widget)
        self.link_widget.setFixedHeight(24)

        # name widget
        self.name_widget = QtWidgets.QFrame()
        _layout.addWidget(self.name_widget)
        self.name_widget.setObjectName("name_widget")
        self.name_widget.setMinimumHeight(25)
        self.name_layout = QtWidgets.QHBoxLayout(self.name_widget)
        self.name_layout.setSpacing(0)
        self.name_layout.setContentsMargins(0,0,0,0)
        #  name button
        self.name_button = QtWidgets.QPushButton()
        self.name_button.setObjectName("title_button")
        self.name_button.setIcon(QtGui.QIcon(resource.get("icons", "task.png")))
        self.name_layout.addWidget(self.name_button)

        # thumbnail widget
        self.thumbnail_widget = QtWidgets.QFrame()
        _layout.addWidget(self.thumbnail_widget)
        self.thumbnail_layout = QtWidgets.QVBoxLayout(self.thumbnail_widget)
        self.thumbnail_layout.setSpacing(0)
        self.thumbnail_layout.setContentsMargins(0,0,0,0)
        self.thumbnail_button = button.ThumbnailButton()
        self.thumbnail_button.setMinimumSize(200, 200)
        self.thumbnail_layout.addWidget(self.thumbnail_button)
        
        # func widget
        self.operation_widget = operationwidget.operationwidget.OperationWidget()
        _layout.addWidget(self.operation_widget)