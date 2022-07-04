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
    updated = QtCore.Signal(list)
    def __init__(self, parent = None):
        super(ProjectEntityWidget, self).__init__(parent)

        self._scale = 0.5

        self._project_entity = None
        self._namespace = ""
        self._output_attr_ids = []

        self._task_widgets = []

        self._build()

        self.update_button.clicked.connect(self._update)

    def _update(self):
        self.updated.emit(self.input_tasks())

    def input_tasks(self):
        _input_tasks = []
        for _task_widget in self._task_widgets:
            _input_task = _task_widget.input_task()
            _input_task["namespace"] = self._namespace
            _input_tasks.append(_input_task)
        return _input_tasks

    def load_project_entity(self, project_entity):
        self._project_entity = project_entity
        _thumbnail = self._project_entity.get_thumbnail()
        if _thumbnail:
            self.thumbnail_button.set_thumbnail(_thumbnail)
        self.name_button.setText(self._project_entity.full_name_code())

    def set_namespace(self, namespace):
        self._namespace = namespace

        self.namespace_button.setText(namespace)

    def add_task_output_attr(self, task_id, output_attr_id, input_attr_id = 0):
        _output_attr = zfused_api.attr.Output(output_attr_id)
        _task = zfused_api.task.Task(task_id)
        _widget = TaskWidget()
        _widget.load(_task.id(), output_attr_id, input_attr_id)
        self.task_layout.addWidget(_widget)
        self._task_widgets.append(_widget)

    def add_output_attr_id(self, output_attr_id, input_attr_id = 0):
        self._output_attr_ids.append(output_attr_id)
        _output_attr = zfused_api.attr.Output(output_attr_id)
        _tasks = self._project_entity.tasks([_output_attr.project_step().id()])
        if _tasks:
            _task = zfused_api.task.Task(_tasks[0].get("Id"))
            _widget = TaskWidget()
            _widget.load(_task.id(), output_attr_id, input_attr_id)
            self.task_layout.addWidget(_widget)
            self._task_widgets.append(_widget)

    def set_extended_version(self, is_extended):
        if not self._task_widgets:
            return
        for _task_widget in self._task_widgets:
            _task_widget.set_extended_version(is_extended)

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
        _layout.setContentsMargins(0,0,0,0)
    
        self.project_entity_widget = QtWidgets.QFrame()
        _layout.addWidget(self.project_entity_widget)
        self.project_entity_layout = QtWidgets.QHBoxLayout(self.project_entity_widget)
        self.project_entity_layout.setSpacing(0)
        self.project_entity_layout.setContentsMargins(0,0,0,0)

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
        self.name_layout.setSpacing(4)
        self.name_layout.setContentsMargins(0,0,0,0)
        self.thumbnail_button = button.ThumbnailButton()
        self.thumbnail_button.setFixedSize(192*self._scale, 108*self._scale)
        self.name_layout.addWidget(self.thumbnail_button)
        self.name_button = QtWidgets.QPushButton()
        self.name_button.setObjectName("title_button")
        self.name_button.setIcon(QtGui.QIcon(resource.get("icons", "task.png")))
        self.name_layout.addWidget(self.name_button)
        self.name_layout.addStretch(True)
        self.namespace_button = QtWidgets.QPushButton()
        self.namespace_button.setObjectName("title_button")
        self.name_layout.addWidget(self.namespace_button)
        self.update_button = QtWidgets.QPushButton(u"更新")
        self.name_layout.addWidget(self.update_button)
        self.update_button.setFixedSize(80,24)

        # task widget
        self.task_widget = QtWidgets.QFrame()
        self.contant_layout.addWidget(self.task_widget)
        self.task_layout = QtWidgets.QVBoxLayout(self.task_widget)
        self.task_layout.setSpacing(2)
        self.task_layout.setContentsMargins(0,0,0,0)

        # self.update_button = QtWidgets.QPushButton()
        # _layout.addWidget(self.update_button)
        # self.update_button.setText(u"更新")
        # self.update_button.setFixedHeight(30)




class TaskWidget(QtWidgets.QFrame):
    def __init__(self, parent=None ):
        super(TaskWidget, self).__init__(parent)

        self.version_combox = None

        self._build()

        self._task_attr_input_id = 0
        self._input_task_id = 0
        self._input_task_attr_output_id = 0

    def input_task(self):
        _input_task = {
                "task_attr_input_id": self._task_attr_input_id,
                "input_task_id": self._input_task_id,
                "input_task_attr_output_id": self._input_task_attr_output_id,
            }
        _text = self.version_combox.currentText()
        if _text == u"无版本":
            _input_task["index"] = -1
        else:
            _input_task["index"] = int(_text)
        return _input_task

    def load(self, input_task_id, input_task_attr_output_id, task_attr_input_id = 0):
        self._task_attr_input_id = task_attr_input_id
        self._input_task_id = input_task_id
        self._input_task_attr_output_id = input_task_attr_output_id

        _task = zfused_api.task.Task(input_task_id)
        _attr = zfused_api.attr.Output(input_task_attr_output_id)
        self.name_label.setText(_task.code())
        self.attr_label.setText(_attr.name_code())
        self.version_combox.addItem(u"无版本")
        _versions = _task.versions()
        if _versions:
            for _version in _versions:
                self.version_combox.addItem("{}".format(_version.get("Index")))
        if task_attr_input_id:
            _input_attr = zfused_api.attr.Input(task_attr_input_id)
            _extended_version = _input_attr.extended_version()
            if _extended_version:
                self.version_combox.setCurrentIndex(self.version_combox.count() - 1)
            else:
                self.version_combox.setCurrentIndex(0)

    def set_extended_version(self, is_extended):
        if is_extended:
            self.version_combox.setCurrentIndex(self.version_combox.count() - 1)
        else:
            self.version_combox.setCurrentIndex(0)

    def _build(self):
        self.setFixedHeight(30)
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        self.name_label = QtWidgets.QLabel("task name")
        _layout.addWidget(self.name_label)

        self.attr_label = QtWidgets.QLabel("attribute name")
        _layout.addWidget(self.attr_label)

        self.version_combox = QtWidgets.QComboBox()
        _layout.addWidget(self.version_combox)
        self.version_combox.setFixedWidth(120)



