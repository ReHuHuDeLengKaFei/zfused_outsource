# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

# from . import inputlistwidget

from . import contain_widget

__all__ = ["AssemblyWidget"]


class AssemblyWidget(QtWidgets.QFrame):
    updated = QtCore.Signal(list)
    def __init__(self, parent = None):
        super(AssemblyWidget, self).__init__(parent)
        self._build()

        self.input_listwidget.updated.connect(self.updated.emit)

    def load_task_id(self, task_id):
        # load task id
        _task_handle = zfused_api.task.Task(task_id)
        _tasks = _task_handle.input_tasks()
        
        self.input_listwidget.load_task_id(task_id)

        if not _tasks:
            self.no_version_widget.setHidden(False)
            self.input_listwidget.setHidden(True)
        else:
            self.no_version_widget.setHidden(True)
            self.input_listwidget.setHidden(False)
    
    def input_tasks(self):
        return self.input_listwidget.input_tasks()

    def _build(self):
        # build widget
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        # receive task
        # self.input_listwidget = inputlistwidget.InputListWidget()
        self.input_listwidget = contain_widget.ContainWidget()
        _layout.addWidget(self.input_listwidget)

        # no version widget
        self.no_version_widget = QtWidgets.QFrame()
        _layout.addWidget(self.no_version_widget)
        self.no_version_layout = QtWidgets.QVBoxLayout(self.no_version_widget)
        self.no_version_layout.setSpacing(0)
        self.no_version_layout.setContentsMargins(0,0,0,0)
        #  message widget 
        self.new_assembly_label = QtWidgets.QPushButton(self.no_version_widget)
        self.new_assembly_label.setIcon(QtGui.QIcon(resource.get("icons","none.png")))
        self.new_assembly_label.setObjectName("new_assembly_button")
        self.new_assembly_label.setText(u"无上游环节引入任务")
        self.no_version_layout.addStretch(True)
        self.no_version_layout.addWidget(self.new_assembly_label)
        self.no_version_layout.addStretch(True)


