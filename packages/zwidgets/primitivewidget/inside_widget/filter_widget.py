# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import sys
import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

__all__ = ["FilterWidget"]

logger = logging.getLogger(__name__)


class FilterWidget(QtWidgets.QFrame):
    _step_changed = QtCore.Signal(int)
    
    switch_step = QtCore.Signal(int)

    selected = QtCore.Signal(list)

    switch_version = QtCore.Signal(bool)

    optimized = QtCore.Signal()

    def __init__(self, parent=None):
        super(FilterWidget, self).__init__(parent)
        self._build()

        self._step_name_id_dict = {}
        self._step_checkboxs = []

        self.update_project_step_button.clicked.connect(self._switch_step)

        self.switch_version_button.clicked.connect(partial(self.switch_version.emit, True))
        self.switch_no_version_button.clicked.connect(partial(self.switch_version.emit, False))

        self.optimize_button.clicked.connect(self.optimized.emit)

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


    def load_elements(self, elements):
        if not elements:
            return

        _element = elements[0]
        _project_id = _element.get("project_id")
        self._load_project_id(_project_id)  

        _project_steps = {}
        for _element in elements:
            _project_step_id = _element.get("project_step_id")
            if _project_step_id not in _project_steps:
                _project_steps[_project_step_id] = []
            _project_steps[_project_step_id].append(_element)

        for _project_step_id, _elements in _project_steps.items():
            # 
            _widget = _ProjectStepWidget()
            _widget.load_datas(_project_step_id, _elements)
            self.current_step_layout.addWidget(_widget)
            _widget.selected.connect(self.selected.emit)
            # _project_step = zfused_api.step.ProjectStep(_project_step_id)
            # _widget = QtWidgets.QLabel(u"{} - {}".format(_project_step.name_code(), len(_elements)))
            # _widget.setStyleSheet("QLabel{font-size: 18px; color: %s;}"%(_project_step.color()))
            # self.current_step_layout.addWidget(_widget)

    def _load_project_id(self, project_id):

        self._clear()

        _project_handle = zfused_api.project.Project(project_id)

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
                # if _step_id == _project_step_id:
                #     _name_checkbox.setChecked(True)
                #     self._step_changed.emit(_step_id)

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

        for i in range(self.asset_step_checkbox_layout.count()):
            self.asset_step_checkbox_layout.itemAt(i).widget().deleteLater()
        for i in range(self.current_step_layout.count()):
            self.current_step_layout.itemAt(i).widget().deleteLater()


    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        # _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # 
        self.operation_widget = QtWidgets.QGroupBox()
        _layout.addWidget(self.operation_widget)
        self.operation_widget.setTitle(u"工具栏")
        self.operation_layout = QtWidgets.QVBoxLayout(self.operation_widget)
        self.operation_layout.setSpacing(0)
        self.operation_layout.setContentsMargins(0,20,0,0)
        
        self.version_widget = QtWidgets.QFrame()
        self.operation_layout.addWidget(self.version_widget)
        self.version_layout = QtWidgets.QHBoxLayout(self.version_widget)
        self.version_layout.setSpacing(4)
        self.version_layout.setContentsMargins(2,2,2,2)
        self.switch_version_button = QtWidgets.QPushButton(u"切换至最新带版本文件")
        self.switch_version_button.setFixedHeight(30)
        self.version_layout.addWidget(self.switch_version_button)
        self.switch_no_version_button = QtWidgets.QPushButton(u"切换至不带版本文件")
        self.switch_no_version_button.setFixedHeight(30)
        self.version_layout.addWidget(self.switch_no_version_button)

        self.optimize_widget = QtWidgets.QFrame()
        _layout.addWidget(self.optimize_widget)
        self.optimize_layout = QtWidgets.QHBoxLayout(self.optimize_widget)
        self.optimize_layout.setSpacing(4)
        self.optimize_layout.setContentsMargins(2,2,2,2)        
        self.optimize_button = QtWidgets.QPushButton()
        self.optimize_button.setText(u"优化场景INSTANCE - 如果不是最终场景，慎重使用")
        self.optimize_layout.addWidget(self.optimize_button)
        self.optimize_button.setFixedHeight(40)

        _layout.addStretch(True)

        # 
        self.current_step_widget = QtWidgets.QGroupBox()
        _layout.addWidget(self.current_step_widget)
        self.current_step_widget.setTitle(u"当前场景")
        self.current_step_layout = QtWidgets.QVBoxLayout(self.current_step_widget)
        self.current_step_layout.setContentsMargins(10,20,10,0)

        # asset task step
        self.step_widget = QtWidgets.QGroupBox()
        _layout.addWidget(self.step_widget)
        self.step_widget.setTitle(u"切换任务步骤")
        self.step_layout = QtWidgets.QVBoxLayout(self.step_widget)
        self.step_layout.setContentsMargins(10,20,10,0)
        # asset step widet 
        self.asset_step_checkbox_widget = QtWidgets.QFrame()
        self.asset_step_checkbox_layout = QtWidgets.QVBoxLayout(self.asset_step_checkbox_widget)
        self.asset_step_checkbox_layout.setContentsMargins(0,0,0,0)
        self.step_layout.addWidget(self.asset_step_checkbox_widget)
        self.step_group = QtWidgets.QButtonGroup(self)
        # update all 
        self.update_project_step_button = QtWidgets.QPushButton()
        self.update_project_step_button.setMinimumSize(100, 40)
        self.update_project_step_button.setText(u"任务步骤批量更新")
        self.step_layout.addWidget(self.update_project_step_button)




class _ProjectStepWidget(QtWidgets.QFrame):
    selected = QtCore.Signal(list)
    def __init__(self, parent = None):
        super(_ProjectStepWidget, self).__init__(parent)

        self._build()

        self._project_step_id = 0
        self._datas = []

        self.select_button.clicked.connect(self._select)
    
    def _select(self):
        self.selected.emit(self._datas)

    def load_datas(self, project_step_id, datas):
        self._project_step_id = project_step_id
        self._datas = datas
        _project_step = zfused_api.step.ProjectStep(self._project_step_id)
        self.project_step_name_label.setText( u"{} - {}".format(_project_step.name_code(), str(len(self._datas))))
        # self.count_label.setText(str(len(self._datas)))
    
    def _build(self):
        self.setFixedHeight(25)
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        self.project_step_name_label = QtWidgets.QLabel("project step name")
        _layout.addWidget(self.project_step_name_label)

        # self.count_label = QtWidgets.QLabel("count")
        # _layout.addWidget(self.count_label)

        self.select_button = QtWidgets.QPushButton("选择")
        _layout.addWidget(self.select_button)
        self.select_button.setFixedSize(80, 24)
