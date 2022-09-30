# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import sys
import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

import zfused_maya.core.record as record

__all__ = ["FilterWidget"]


logger = logging.getLogger(__name__)


class FilterWidget(QtWidgets.QFrame):
    _step_changed = QtCore.Signal(int)
    
    switch_step = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(FilterWidget, self).__init__(parent)
        self._build()

        self._step_name_id_dict = {}
        self._step_checkboxs = []

        self.update_project_step_button.clicked.connect(self._switch_step)
        #self._load()

    def _switch_step(self):
        _step_id = 0
        for _checkbox in self._step_checkboxs:
            if _checkbox.isChecked():
                _step_id = self._step_name_id_dict[_checkbox.text()]
        if _step_id:
            self.switch_step.emit(_step_id)

    def load_project_id(self, project_id):
        """ 加载项目资产类型和任务步骤
        
        :rtype: None
        """
        pass

    def _asset_type_ids(self):
        _type_ids = []
        for _checkbox in self._type_checkboxs:
            if _checkbox.isChecked():
                _type_ids.append(self._type_name_id_dict[_checkbox.text()])
        self.asset_type_changed.emit(_type_ids)

    def _task_step_id(self):
        for _checkbox in self._step_checkboxs:
            if _checkbox.isChecked():
                self._step_changed.emit(self._step_name_id_dict[_checkbox.text()])

    def load_config(self):
        # clear asset type item
        self._clear()
        # get current project id
        _project_id = record.current_project_id()
        if not _project_id:
            return
        _project_handle = zfused_api.project.Project(_project_id)
        # interface
        _interface = record.Interface()
        _project_step_id = _interface.get("element_manage_project_step_id")

        _step_ids = _project_handle.task_step_ids("asset")
        if _step_ids:
            for _step_id in _step_ids:
                _step_handle = zfused_api.step.ProjectStep(_step_id)
                _name = _step_handle.name_code()
                self._step_name_id_dict[_name] = _step_id
                _name_checkbox = QtWidgets.QCheckBox()
                _name_checkbox.setText(_name)
                self.asset_step_checkbox_layout.addWidget(_name_checkbox)
                self.step_group.addButton(_name_checkbox)
                self._step_checkboxs.append(_name_checkbox)
                _name_checkbox.stateChanged.connect(self._task_step_id)
                if _step_id == _project_step_id:
                    _name_checkbox.setChecked(True)
                    self._step_changed.emit(_step_id)

    def _clear(self):
        """清除资产类型和任务步骤
        
        :rtype: None
        """
        # 清除资产类型
        self._type_name_id_dict = {}
        self._type_checkboxs = []
        # _childrens = self.filter_type_widget.findChildren(QtWidgets.QCheckBox)
        # if not _childrens:
        #     return
        # for _child in _childrens:
        #     self.filter_project_step_checkbox_layout.removeWidget(_child)
        #     _child.deleteLater()

        # 清除任务步骤
        self._step_name_id_dict = {}
        self._step_checkboxs = []


    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)

        # asset task step
        self.step_widget = QtWidgets.QFrame()
        _layout.addWidget(self.step_widget)
        self.step_layout = QtWidgets.QVBoxLayout(self.step_widget)
        self.step_layout.setSpacing(0)
        self.step_layout.setContentsMargins(0,0,0,0)

        # asset
        self.asset_step_name_button = QtWidgets.QPushButton()
        self.asset_step_name_button.setMaximumHeight(25)
        self.asset_step_name_button.setText(language.word("task step for asset"))
        self.asset_step_name_button.setObjectName("attr_name_button")
        self.asset_step_name_button.setIcon(QtGui.QIcon(resource.get("icons","asset.png")))
        self.asset_step_name_button.hide()
        self.step_layout.addWidget(self.asset_step_name_button)
        self.asset_step_checkbox_widget = QtWidgets.QFrame()
        self.asset_step_checkbox_layout = QtWidgets.QVBoxLayout(self.asset_step_checkbox_widget)
        self.asset_step_checkbox_layout.setContentsMargins(20,0,0,0)
        self.step_layout.addWidget(self.asset_step_checkbox_widget)

        self.step_group = QtWidgets.QButtonGroup(self)
        _layout.addStretch(True)

        # update all 
        self.update_project_step_button = QtWidgets.QPushButton()
        self.update_project_step_button.setMinimumSize(100, 40)
        self.update_project_step_button.setText(u"任务步骤批量更新")
        _layout.addWidget(self.update_project_step_button)