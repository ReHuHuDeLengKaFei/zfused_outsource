# coding:utf-8
# --author-- lanhua.zhou

""" 
    assembly management load asset assembly definition file 
"""
from __future__ import print_function

import sys
import os
import logging

import maya.cmds as cmds
import maya.mel as mm

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

__all__ = ["OperationWidget"]

logger = logging.getLogger(__name__)


class OperationWidget(QtWidgets.QFrame):
    gpu_import = QtCore.Signal(str)
    def __init__(self, parent=None):
        super(OperationWidget, self).__init__(parent)
        self._build()

        self._task_id = 0

        self.import_gpu_button.clicked.connect(self._import_gpu)

    def _import_gpu(self):
        _task = zfused_api.task.Task(self._task_id)
        _production_path = _task.production_path()
        _gpu_path = "{}/gpu/{}.abc".format(_production_path, _task.file_code())
        if os.path.isfile(_gpu_path):
            self.gpu_import.emit(_gpu_path)

    def load_task_id(self, task_id):
        self._task_id = task_id
        _task = zfused_api.task.Task(task_id)
        self.infomation_label.setText(_task.name())

        _production_path = _task.production_path()
        _gpu_path = "{}/gpu/{}.abc".format(_production_path, _task.file_code())
        if os.path.isfile(_gpu_path):
            self.import_gpu_button.setStyleSheet("QPushButton{background-color:#3FA847}")
        else:
            self.import_gpu_button.setStyleSheet("QPushButton{background-color:#FF0000}")

    def _build(self):
        self.setFixedHeight(40)
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        # infomation
        self.infomation_label = QtWidgets.QLabel()
        _layout.addWidget(self.infomation_label)
        _layout.addStretch(True)

        # import button
        self.import_gpu_button = QtWidgets.QPushButton()
        self.import_gpu_button.setFixedSize(100, 36)
        self.import_gpu_button.setText(u"导入GPU文件")
        _layout.addWidget(self.import_gpu_button)