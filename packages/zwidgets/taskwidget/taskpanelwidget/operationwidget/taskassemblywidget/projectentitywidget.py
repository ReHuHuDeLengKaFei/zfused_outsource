# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import time
import datetime
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import button



class ProjectEntityWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(ProjectEntityWidget, self).__init__(parent)

        self._scale = 0.8

        self._project_entity = None
        self._namespace = ""
        self._output_attr_ids = []

        self._build()

    def load_project_entity(self, project_entity):
        self._project_entity = project_entity
        _thumbnail = self._project_entity.get_thumbnail()
        if _thumbnail:
            self.thumbnail_button.set_thumbnail(_thumbnail)
        self.name_button.setText(self._project_entity.full_name_code())

    def set_namespace(self, namespace):
        self._namespace = namespace

        self.namespace_button.setText(namespace)

    def add_task_output_attr(self, task_id, output_attr_id):

        _button = QtWidgets.QPushButton()
        _button.setFixedHeight(50)

        _output_attr = zfused_api.attr.Output(output_attr_id)

        _task = zfused_api.task.Task(task_id)
        _button.setText( "{} - {}".format(_task.code(), _output_attr.code()))
        self.task_layout.addWidget(_button)


    def add_output_attr_id(self, output_attr_id):
        self._output_attr_ids.append(output_attr_id)
        
        _output_attr = zfused_api.attr.Output(output_attr_id)

        _button = QtWidgets.QPushButton()
        _button.setFixedHeight(50)

        _tasks = self._project_entity.tasks([_output_attr.project_step().id()])
        if _tasks:
            _task = zfused_api.task.Task(_tasks[0].get("Id"))
            _button.setText(_task.code())
            self.task_layout.addWidget(_button)

    def load(self, task_id, output_attr_id):
        _task = zfused_api.task.Task(task_id)
        _project_step = _task.project_step()
        _project_entity = _task.project_entity()

        self.name_button.setText(_task.name())
        _thumbnail = _project_entity.get_thumbnail()
        if not _thumbnail:
            _thumbnail = _task.get_thumbnail()
        if _thumbnail:
            self.thumbnail_button.set_thumbnail(_thumbnail)

        self.project_entity_button.setIcon(QtGui.QIcon(resource.get("icons", "{}.png".format(_project_entity.object()))))
        self.project_entity_button.setText(_project_entity.full_name())


    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)
    
        self.project_entity_widget = QtWidgets.QFrame()
        _layout.addWidget(self.project_entity_widget)
        self.project_entity_layout = QtWidgets.QHBoxLayout(self.project_entity_widget)
        self.project_entity_layout.setSpacing(0)
        self.project_entity_layout.setContentsMargins(0,0,0,0)

        self.thumbnail_button = button.ThumbnailButton()
        self.thumbnail_button.setFixedSize(192*self._scale, 108*self._scale)
        self.project_entity_layout.addWidget(self.thumbnail_button)

        self.contant_widget = QtWidgets.QFrame()
        self.project_entity_layout.addWidget(self.contant_widget)
        self.contant_layout = QtWidgets.QVBoxLayout(self.contant_widget)
        self.contant_layout.setSpacing(0)
        self.contant_layout.setContentsMargins(0,0,0,0)

        self.name_widget = QtWidgets.QFrame()
        self.contant_layout.addWidget(self.name_widget)
        self.name_widget.setObjectName("operation_frame")
        self.name_widget.setFixedHeight(30)
        self.name_layout = QtWidgets.QHBoxLayout(self.name_widget)
        self.name_layout.setSpacing(0)
        self.name_layout.setContentsMargins(0,0,0,0)
        self.name_button = QtWidgets.QPushButton()
        self.name_button.setObjectName("title_button")
        self.name_button.setIcon(QtGui.QIcon(resource.get("icons", "task.png")))
        self.name_layout.addWidget(self.name_button)
        self.name_layout.addStretch(True)
        self.namespace_button = QtWidgets.QPushButton()
        self.namespace_button.setObjectName("title_button")
        self.name_layout.addWidget(self.namespace_button)

        # task widget
        self.task_widget = QtWidgets.QFrame()
        self.contant_layout.addWidget(self.task_widget)
        self.task_layout = QtWidgets.QHBoxLayout(self.task_widget)
        self.task_layout.setSpacing(2)
        self.task_layout.setContentsMargins(0,0,0,0)

        # self.update_button = QtWidgets.QPushButton()
        # _layout.addWidget(self.update_button)
        # self.update_button.setText(u"更新")
        # self.update_button.setFixedHeight(30)