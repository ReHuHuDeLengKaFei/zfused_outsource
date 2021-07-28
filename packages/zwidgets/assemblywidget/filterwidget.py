# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import sys
import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

__all__ = ["FilterWidget"]


logger = logging.getLogger(__name__)


class FilterWidget(QtWidgets.QFrame):
    assembly_type_changed = QtCore.Signal(list)
    assembly_step_changed = QtCore.Signal(int)
    def __init__(self, parent=None):
        super(FilterWidget, self).__init__(parent)
        self._build()

        self._project_id = 0

        self._type_name_id_dict = {}
        self._type_checkboxs = []
        self._step_name_id_dict = {}
        self._step_checkboxs = []

    def _assembly_type_ids(self):
        _type_ids = []
        for _checkbox in self._type_checkboxs:
            if _checkbox.isChecked():
                _type_ids.append(self._type_name_id_dict[_checkbox.text()])
        self.assembly_type_changed.emit(_type_ids)

    def _assembly_task_step_id(self):
        for _checkbox in self._step_checkboxs:
            if _checkbox.isChecked():
                self.assembly_step_changed.emit(self._step_name_id_dict[_checkbox.text()])

    def load_project_id(self, project_id):
        # clear assembly type item
        self._clear()
        # get current project id
        if not project_id:
            return
        self._project_id = project_id
        _project = zfused_api.project.Project(self._project_id)
        
        # # assembly type
        # _project = zfused_api.project.Project(self._project_id)
        # _assembly_type_ids = _project.assembly_type_ids()
        # if _assembly_type_ids:
        #     for _assembly_type_id in _assembly_type_ids:
        #         _assembly_type_handle = zfused_api.types.Types(_assembly_type_id)
        #         _name = _assembly_type_handle.name_code()
        #         self._type_name_id_dict[_name] = _assembly_type_id
        #         _name_checkbox = QtWidgets.QCheckBox()
        #         _name_checkbox.setText(_name)
        #         self.filter_type_checkbox_layout.addWidget(_name_checkbox)
        #         self._type_checkboxs.append(_name_checkbox)
        #         _name_checkbox.stateChanged.connect(self._assembly_type_ids)

        # assembly task step
        _step_ids = _project.task_step_ids("assembly")
        if _step_ids:
            for _step_id in _step_ids:
                _step_handle = zfused_api.step.ProjectStep(_step_id)
                _name = _step_handle.name_code()
                self._step_name_id_dict[_name] = _step_id
                _name_checkbox = QtWidgets.QCheckBox()
                _name_checkbox.setText(_name)
                self.step_checkbox_layout.addWidget(_name_checkbox)
                self.step_group.addButton(_name_checkbox)
                self._step_checkboxs.append(_name_checkbox)
                _name_checkbox.stateChanged.connect(self._assembly_task_step_id)

                # if _step_id == _project_step_id:
                #     _name_checkbox.setChecked(True)

    def _clear(self):
        """清除资产类型和任务步骤
        
        :rtype: None
        """
        # # 清除资产类型
        # self._type_name_id_dict = {}
        # self._type_checkboxs = []
        # _childrens = self.filter_type_widget.findChildren(QtWidgets.QCheckBox)
        # if not _childrens:
        #     return
        # for _child in _childrens:
        #     self.filter_type_checkbox_layout.removeWidget(_child)
        #     _child.deleteLater()

        # 清除任务步骤
        self._step_name_id_dict = {}
        self._step_checkboxs = []
        _childrens = self.step_checkbox_widget.findChildren(QtWidgets.QCheckBox)
        if not _childrens:
            return
        for _child in _childrens:
            self.step_checkbox_layout.removeWidget(_child)
            _child.deleteLater()

    def _build(self):
        self.setMaximumWidth(200)
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # # filter type widget
        # self.filter_type_widget = QtWidgets.QFrame()
        # _layout.addWidget(self.filter_type_widget)
        # self.filter_type_layout = QtWidgets.QVBoxLayout(self.filter_type_widget)
        # self.filter_type_layout.setSpacing(0)
        # self.filter_type_layout.setContentsMargins(0,0,0,0)
        # #  title button
        # self.filter_type_name_button = QtWidgets.QPushButton()
        # self.filter_type_name_button.setObjectName("title_button")
        # self.filter_type_name_button.setMaximumHeight(25)
        # self.filter_type_name_button.setText(u"资产类型检索")
        # self.filter_type_name_button.setIcon(QtGui.QIcon(resource.get("icons","filter.png")))
        # self.filter_type_layout.addWidget(self.filter_type_name_button)
        # #  type widget
        # self.filter_type_checkbox_widget = QtWidgets.QFrame()
        # self.filter_type_layout.addWidget(self.filter_type_checkbox_widget)
        # self.filter_type_checkbox_layout = QtWidgets.QVBoxLayout(self.filter_type_checkbox_widget)
        # self.filter_type_checkbox_layout.setContentsMargins(20,0,0,0)

        # task step
        self.step_widget = QtWidgets.QFrame()
        _layout.addWidget(self.step_widget)
        self.step_layout = QtWidgets.QVBoxLayout(self.step_widget)
        self.step_layout.setSpacing(0)
        self.step_layout.setContentsMargins(0,0,0,0)
        self.step_name_button = QtWidgets.QPushButton()
        self.step_name_button.setObjectName("title_button")
        self.step_name_button.setMaximumHeight(25)
        self.step_name_button.setText(u"场景装配任务步骤")
        self.step_name_button.setIcon(QtGui.QIcon(resource.get("icons","filter.png")))
        self.step_layout.addWidget(self.step_name_button)
        # step checkbox widget
        self.step_checkbox_widget = QtWidgets.QFrame()
        self.step_checkbox_layout = QtWidgets.QVBoxLayout(self.step_checkbox_widget)
        self.step_checkbox_layout.setContentsMargins(20,0,0,0)
        self.step_group = QtWidgets.QButtonGroup(self.step_checkbox_widget)
        self.step_layout.addWidget(self.step_checkbox_widget)

        _layout.addStretch(True)