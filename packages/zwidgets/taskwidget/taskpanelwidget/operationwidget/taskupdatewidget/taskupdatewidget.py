# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,transfer

from ..taskreceivewidget import assemblywidget

logger = logging.getLogger(__name__)



class TaskUpdateWidget(QtWidgets.QFrame):
    received = QtCore.Signal(str, int, list)
    def __init__(self, parent = None):
        super(TaskUpdateWidget, self).__init__(parent)
        self._build()

        self._task_id = 0

        self.assembly_widget.updated.connect(self._update_file)
        self.update_button.clicked.connect(self._update_all)

    def load_task_id(self, task_id):
        """ load task id
        :rtype: None
        """
        if not task_id:
            return
        self._task_id = task_id
        self.assembly_widget.load_task_id(task_id)

    def _update_file(self, tasks):
        self.received.emit("update", self._task_id, tasks)
    
    def _update_all(self):
        _input_tasks = self.assembly_widget.input_tasks()
        self.received.emit("update", self._task_id, _input_tasks)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        # assembly widget
        self.assembly_widget = assemblywidget.AssemblyWidget()
        _layout.addWidget(self.assembly_widget)

        # receive widget
        self.update_widget = QtWidgets.QFrame()
        _layout.addWidget(self.update_widget)
        self.update_widget.setObjectName("update_widget")
        self.update_widget.setMinimumHeight(40)
        self.update_layout = QtWidgets.QHBoxLayout(self.update_widget)
        self.update_layout.setSpacing(2)
        self.update_layout.setContentsMargins(6,6,6,6)

        self.update_layout.addStretch(True)
        #  receive button
        self.update_button = QtWidgets.QPushButton()
        self.update_button.setMinimumHeight(30)
        self.update_button.setObjectName("update_button")
        self.update_button.setMinimumWidth(80)
        self.update_button.setIcon(QtGui.QIcon(resource.get("icons","receive.png")))
        self.update_button.setText(u"全部更新")
        self.update_layout.addWidget(self.update_button)