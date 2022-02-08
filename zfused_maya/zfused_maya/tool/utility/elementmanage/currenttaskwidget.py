# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import button

import zfused_maya.core.record as record

__all__ = ["CurrentTaskWidget"]

logger = logging.getLogger(__name__)


class CurrentTaskWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(CurrentTaskWidget, self).__init__()
        self._build()

        self._project_id = 0
        self._entity_type = ""
        self._entity_id = 0
        self._task_id = 0

        # self._timer = QtCore.QTimer()
        self.refresh()

    def refresh(self):
        # project 
        _project_id = record.current_project_id()
        if _project_id:
            _project_handle = zfused_api.project.Project(_project_id)
            self.project_button.setText(_project_handle.name_code())
        else:
            self.project_button.setText("未设置项目") 
        # task
        _task_id = record.current_task_id()
        if _task_id:
            _task_handle = zfused_api.task.Task(_task_id)
            _entity_handle = _task_handle.project_entity()
            self.link_button.setText(_entity_handle.name_code())
            self.task_button.setText(_task_handle.name())
        else:
            self.link_button.setText("未设置当前任务")
            self.task_button.setText("未设置当前任务")

    def _build(self):
        """ build operation widget

        """
        self.setMaximumHeight(40)

        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,4,2,2)

        # check widget
        # check current file
        self.check_file_button = QtWidgets.QPushButton()
        self.check_file_button.setMinimumSize(100, 40)
        self.check_file_button.setText(u"检测当前文件")

        # task widget
        self.task_widget = QtWidgets.QFrame()
        _layout.addWidget(self.task_widget)
        self.task_layout = QtWidgets.QHBoxLayout(self.task_widget)
        self.task_layout.setSpacing(2)
        self.task_layout.setContentsMargins(2,2,2,2)
        # project
        self.project_button = button.IconButton( self, 
                                                 resource.get("icons", "project.png"),
                                                 resource.get("icons", "project.png"),
                                                 resource.get("icons", "project.png") )
        self.task_layout.addWidget(self.project_button)
        self.project_button.setText("未设置项目") 
        self.project_button.setObjectName("task_link_button")
        # entity name code
        self.link_button = button.IconButton( self, 
                                                resource.get("icons", "link.png"),
                                                resource.get("icons", "link.png"),
                                                resource.get("icons", "link.png") )
        self.task_layout.addWidget(self.link_button)
        self.link_button.setText("未设置当前任务")
        self.link_button.setObjectName("task_link_button")
        # task 
        self.task_button = button.IconButton( self, 
                                              resource.get("icons", "task.png"),
                                              resource.get("icons", "task.png"),
                                              resource.get("icons", "task.png") )
        self.task_layout.addWidget(self.task_button)
        self.task_button.setText("未设置当前任务")
        self.task_button.setObjectName("task_link_button")
        self.task_layout.addStretch(True)

        # _layout.addStretch(True)