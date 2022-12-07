# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import sys
import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource


logger = logging.getLogger(__name__)



class FilterWidget(QtWidgets.QFrame):
    _step_changed = QtCore.Signal(list)
    def __init__(self, parent=None):
        super(FilterWidget, self).__init__(parent)
        self._build()

        self._project_id = 0

        self._step_name_id_dict = {}
        self._step_checkboxs = []

    def _task_step_id(self):
        _ids = []
        for _checkbox in self._step_checkboxs:
            if _checkbox.isChecked():
                # self._step_changed.emit([self._step_name_id_dict[_checkbox.text()]])
                _ids.append(self._step_name_id_dict[_checkbox.text()])
        self._step_changed.emit(_ids)

    def load_project_id(self, project_id):

        self._clear()

        if not project_id:
            return
            
        self._project_id = project_id
        _project = zfused_api.project.Project(self._project_id)
        
        # asset task step
        _step_ids = _project.task_step_ids("asset")
        if _step_ids:
            for _step_id in _step_ids:
                _step_handle = zfused_api.step.ProjectStep(_step_id)
                _name = _step_handle.name_code()
                self._step_name_id_dict[_name] = _step_id
                _name_checkbox = QtWidgets.QCheckBox()
                _name_checkbox.setText(_name)
                self.asset_step_checkbox_layout.addWidget(_name_checkbox)
                # self.step_group.addButton(_name_checkbox)
                self._step_checkboxs.append(_name_checkbox)
                _name_checkbox.stateChanged.connect(self._task_step_id)
        # assembly task step
        _step_ids = _project.task_step_ids("assembly")
        if _step_ids:
            for _step_id in _step_ids:
                _step_handle = zfused_api.step.ProjectStep(_step_id)
                _name = _step_handle.name_code()
                self._step_name_id_dict[_name] = _step_id
                _name_checkbox = QtWidgets.QCheckBox()
                _name_checkbox.setText(_name)
                self.assembly_step_checkbox_layout.addWidget(_name_checkbox)
                # self.step_group.addButton(_name_checkbox)
                self._step_checkboxs.append(_name_checkbox)
                _name_checkbox.stateChanged.connect(self._task_step_id)
        # shot task step
        _step_ids = _project.task_step_ids("shot")
        if _step_ids:
            for _step_id in _step_ids:
                _step_handle = zfused_api.step.ProjectStep(_step_id)
                _name = _step_handle.name_code()
                self._step_name_id_dict[_name] = _step_id
                _name_checkbox = QtWidgets.QCheckBox()
                _name_checkbox.setText(_name)
                self.shot_step_checkbox_layout.addWidget(_name_checkbox)
                # self.step_group.addButton(_name_checkbox)
                self._step_checkboxs.append(_name_checkbox)
                _name_checkbox.stateChanged.connect(self._task_step_id)
        # _asset_type_ids = _project.asset_type_ids()
        # self.type_filter_widget.load_type_ids(_asset_type_ids)

        # _step_ids = _project.task_step_ids("asset")
        # self.project_step_filter_widget.load_project_step_ids(_step_ids)

    def _clear(self):
        """清除资产类型和任务步骤
        :rtype: None
        """
        # 清除任务步骤
        self._step_name_id_dict = {}
        self._step_checkboxs = []

        # asset 
        _childrens = self.asset_step_checkbox_widget.findChildren(QtWidgets.QCheckBox)
        if not _childrens:
            return
        for _child in _childrens:
            self.asset_step_checkbox_widget.removeWidget(_child)
            _child.deleteLater()
        # assembly 
        _childrens = self.assembly_step_checkbox_widget.findChildren(QtWidgets.QCheckBox)
        if not _childrens:
            return
        for _child in _childrens:
            self.assembly_step_checkbox_widget.removeWidget(_child)
            _child.deleteLater()
        # shot 
        _childrens = self.shot_step_checkbox_widget.findChildren(QtWidgets.QCheckBox)
        if not _childrens:
            return
        for _child in _childrens:
            self.shot_step_checkbox_widget.removeWidget(_child)
            _child.deleteLater()

    def _build(self):
        self.setMaximumWidth(200)
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        self.step_group = QtWidgets.QButtonGroup(self)

        # asset task step
        self.step_widget = QtWidgets.QFrame()
        _layout.addWidget(self.step_widget)
        self.step_layout = QtWidgets.QVBoxLayout(self.step_widget)
        self.step_layout.setSpacing(0)
        self.step_layout.setContentsMargins(0,0,0,0)
        # asset
        self.asset_step_name_button = QtWidgets.QPushButton()
        self.asset_step_name_button.setObjectName("title_button")
        self.asset_step_name_button.setMaximumHeight(25)
        self.asset_step_name_button.setText(u"资产")
        self.asset_step_name_button.setIcon(QtGui.QIcon(resource.get("icons","filter.png")))
        self.step_layout.addWidget(self.asset_step_name_button)
        self.asset_step_checkbox_widget = QtWidgets.QFrame()
        self.asset_step_checkbox_layout = QtWidgets.QVBoxLayout(self.asset_step_checkbox_widget)
        self.asset_step_checkbox_layout.setContentsMargins(20,0,0,0)
        self.step_layout.addWidget(self.asset_step_checkbox_widget)
        # assembly
        self.assembly_step_name_button = QtWidgets.QPushButton()
        self.assembly_step_name_button.setObjectName("title_button")
        self.assembly_step_name_button.setMaximumHeight(25)
        self.assembly_step_name_button.setText(u"场景集合")
        self.assembly_step_name_button.setIcon(QtGui.QIcon(resource.get("icons","filter.png")))
        self.step_layout.addWidget(self.assembly_step_name_button)
        self.assembly_step_checkbox_widget = QtWidgets.QFrame()
        self.assembly_step_checkbox_layout = QtWidgets.QVBoxLayout(self.assembly_step_checkbox_widget)
        self.assembly_step_checkbox_layout.setContentsMargins(20,0,0,0)
        self.step_layout.addWidget(self.assembly_step_checkbox_widget)
        # shot
        self.shot_step_name_button = QtWidgets.QPushButton()
        self.shot_step_name_button.setObjectName("title_button")
        self.shot_step_name_button.setMaximumHeight(25)
        self.shot_step_name_button.setText(u"镜头")
        self.shot_step_name_button.setIcon(QtGui.QIcon(resource.get("icons","filter.png")))
        self.step_layout.addWidget(self.shot_step_name_button)
        self.shot_step_checkbox_widget = QtWidgets.QFrame()
        self.shot_step_checkbox_layout = QtWidgets.QVBoxLayout(self.shot_step_checkbox_widget)
        self.shot_step_checkbox_layout.setContentsMargins(20,0,0,0)
        self.step_layout.addWidget(self.shot_step_checkbox_widget)

        _layout.addStretch(True)