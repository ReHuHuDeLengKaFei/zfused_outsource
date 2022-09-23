# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import time
import datetime
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import button,progress


from . import project_entity_widget



class ContainWidget(QtWidgets.QFrame):
    updated = QtCore.Signal(list)
    def __init__(self, parent = None):
        super(ContainWidget, self).__init__(parent)
        self._build()
        self._task_id = 0

        self.version_button.clicked.connect(partial(self._extended_version, True))
        self.no_version_button.clicked.connect(partial(self._extended_version, False))

        self.self_widget.updated.connect(self.updated.emit)
        self.asset_widget.updated.connect(self.updated.emit)
        self.assembly_widget.updated.connect(self.updated.emit)

    def _extended_version(self, is_extended):
        self.self_widget.set_extended_version(is_extended)
        self.asset_widget.set_extended_version(is_extended)
        self.assembly_widget.set_extended_version(is_extended)

    @zfused_api.reset
    def load_task_id(self, task_id):
        _st = time.time()
        self._task_id = task_id
        self.self_widget.load_task_id(task_id)
        self.asset_widget.load_task_id(task_id)
        self.assembly_widget.load_task_id(task_id)

    def input_tasks(self):
        _input_tasks = []
        _input_tasks += self.self_widget.input_tasks()
        _input_tasks += self.asset_widget.input_tasks()
        _input_tasks += self.assembly_widget.input_tasks()
        return _input_tasks

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0,4,0,0)

        self.operation_widget = QtWidgets.QFrame()
        _layout.addWidget(self.operation_widget)
        self.operation_widget.setFixedHeight(20)
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_widget)
        self.operation_layout.setSpacing(4)
        self.operation_layout.setContentsMargins(2,0,2,0)
        self.operation_layout.addStretch(True)
        self.version_button = QtWidgets.QPushButton("最新版本")
        self.operation_layout.addWidget(self.version_button)
        self.version_button.setFixedSize(100, 20)
        self.no_version_button = QtWidgets.QPushButton("无版本")
        self.operation_layout.addWidget(self.no_version_button)
        self.no_version_button.setFixedSize(100, 20)
        self.operation_layout.addStretch(True)

        self.scroll_widget = QtWidgets.QScrollArea()
        _layout.addWidget(self.scroll_widget)
        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setBackgroundRole(QtGui.QPalette.NoRole)
        self.scroll_widget.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.body_widget = QtWidgets.QFrame()
        self.scroll_widget.setWidget(self.body_widget)
        self.body_layout = QtWidgets.QVBoxLayout(self.body_widget)

        self.self_widget = SelfWidget()
        self.body_layout.addWidget(self.self_widget)

        self.asset_widget = AssetWidget()
        self.body_layout.addWidget(self.asset_widget)

        self.assembly_widget = AssemblyWidget()
        self.body_layout.addWidget(self.assembly_widget)

        self.body_layout.addStretch(True)



class RelyWidget(QtWidgets.QFrame):
    updated = QtCore.Signal(list)
    def __init__(self, parent = None):
        super(RelyWidget, self).__init__(parent)
        # self._title = "rely"
        self._build()

        self._project_entity_widgets = []

        self.all_selected_checkbox.stateChanged.connect(self._all_selected)
    
    def _all_selected(self, is_selected):
        if self._project_entity_widgets:
            for _project_entity_widget in self._project_entity_widgets:
                _project_entity_widget.set_selected(is_selected)

    def set_extended_version(self, is_extended):
        if not self._project_entity_widgets:
            return
        for _project_entity_widget in self._project_entity_widgets:
            _project_entity_widget.set_extended_version(is_extended)

    def input_tasks(self):
        _input_tasks = []
        if self._project_entity_widgets:
            for _project_entity_widget in self._project_entity_widgets:
                _input_tasks += _project_entity_widget.input_tasks()
        return _input_tasks

    def _set_contant_show(self, is_show):
        self.contant_widget.setHidden(not is_show)

    def load_task_id(self, task_id):
        self._project_entity_widgets = []

        _task = zfused_api.task.Task(task_id)       
        
        for i in range(self.contant_layout.count()):
            self.contant_layout.itemAt(i).widget().deleteLater()

        # _project_entity = _task.project_entity()
        # self.title_button.setText(_project_entity.name_code())

        _project_step = _task.project_step()
        # get self input task
        _input_attrs = _project_step.input_attrs()
        _attrs = []
        if _input_attrs:
            for _input_attr in _input_attrs:
                _rely = _input_attr.rely()
                if _rely == self._title:
                    _attrs.append(_input_attr)
        if _attrs:
            self.showNormal()
        else:
            self.hide()

        return _attrs


    def add_widget(self, widget):
        self.contant_layout.addWidget(widget)


    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,0,2,0)

        self.title_widget = QtWidgets.QFrame()
        _layout.addWidget(self.title_widget)
        self.title_layout = QtWidgets.QHBoxLayout(self.title_widget)
        self.title_layout.setSpacing(2)
        self.title_layout.setContentsMargins(2,0,2,0)
        self.title_button = QtWidgets.QLabel()
        self.title_button.setText(self._title)
        # self.title_button.setObjectName("title_button")
        self.title_layout.addWidget(self.title_button)

        self.title_layout.addStretch(True)

        self.all_selected_checkbox = QtWidgets.QCheckBox("全选")
        self.title_layout.addWidget(self.all_selected_checkbox)
        self.all_selected_checkbox.setChecked(True)

        self.view_checkbox = QtWidgets.QCheckBox()
        self.view_checkbox.setChecked(True)
        self.view_checkbox.stateChanged.connect(self._set_contant_show)
        self.view_checkbox.setText(u"显示")
        self.title_layout.addWidget(self.view_checkbox)
        self.view_checkbox.hide()

        self.contant_widget = QtWidgets.QFrame()
        _layout.addWidget(self.contant_widget)
        self.contant_layout = QtWidgets.QVBoxLayout(self.contant_widget)
        self.contant_layout.setSpacing(2)
        self.contant_layout.setContentsMargins(2,0,2,0)



class SelfWidget(RelyWidget):
    def __init__(self, parent = None):
        
        self._title = "self"

        super(SelfWidget, self).__init__(parent)

        

        # self._build()

    def load_task_id(self, task_id):
        _attrs = super(SelfWidget, self).load_task_id(task_id)
        _task = zfused_api.task.Task(task_id)       
        _project_entity = _task.project_entity()
        if _attrs:
            for _index, _attr in enumerate(_attrs):
                _conn_attr = zfused_api.zFused.get("attr_conn", filter = {"AttrInputId": _attr.id()})
                if _conn_attr:
                    _conn_attr = _conn_attr[0]
                    _attr = zfused_api.attr.Output(_conn_attr.get("AttrOutputId"))
                    _tasks = _project_entity.tasks([_attr.project_step_id()])
                    if not _tasks:
                        continue
                    _task = _tasks[0]
                    _widget = project_entity_widget.ProjectEntityWidget()
                    _widget.updated.connect(self.updated.emit)
                    _widget.load_project_entity(_project_entity)
                    # _widget.add_output_attr_id(_attr.id())
                    _widget.add_task_output_attr( _task.get("Id"),  _attr.id(), _conn_attr.get("AttrInputId"))
                    self.add_widget(_widget)
                    self._project_entity_widgets.append(_widget)




class AssetWidget(RelyWidget):
    def __init__(self, parent = None):
        
        self._title = "asset"

        super(AssetWidget, self).__init__(parent)
        # self._build()

    @progress.progress(u"分析资产...")
    def load_task_id(self, task_id):
        _attrs = super(AssetWidget, self).load_task_id(task_id)
        self.title_button.setText(language.word(self._title))
        
        if not _attrs:
            return

        _task = zfused_api.task.Task(task_id)   
        _project_entity = _task.project_entity()
        
        _st = time.time()

        # get relative asset
        _relative_assets = zfused_api.zFused.get("relative", filter = { "SourceObject": "asset", "TargetObject": _project_entity.object(), "TargetId": _project_entity.id() })
        if not _relative_assets:
            return
                
        _asset_ids = [ _relative_asset.get("SourceId") for _relative_asset in _relative_assets ]
        _asset_widget = {}

        _input_tasks = []
        _task_input_tasks = _task.input_tasks()
        if not _task_input_tasks:
            return

        progress.set_range(0, len(_task_input_tasks))
        _index = 0

        for _conn_id, _task_list in _task_input_tasks.items():

            
            progress.set_label_text(u"{}/{} - 分析资产".format(_index + 1, len(_task_input_tasks)))
            progress.set_value(_index)
            _index += 1

            # _input_tasks += [_task for _task in _task_list]
            _conn_attr = zfused_api.zFused.get_one("attr_conn", _conn_id)
            if not _conn_attr:
                return

            # for _conn_attr in _conn_attrs:
            _mode = _conn_attr.get("Mode")
            _attr = zfused_api.attr.Output(_conn_attr.get("AttrOutputId"))
            
            for _input_task in _task_list:
                if _input_task.get("ProjectStepId") != _attr.project_step_id():
                    continue
                if not _input_task.get("NameSpace"):
                    continue
                
                for _relative_asset in _relative_assets:
                    _namespace = _relative_asset.get("NameSpace")
                    _asset_id = _relative_asset.get("SourceId")
                    _asset = zfused_api.asset.Asset(_asset_id)

                    _asset_key = "{}_{}".format(_asset_id, _namespace)

                    if _asset_key not in _asset_widget:
                        _widget = project_entity_widget.ProjectEntityWidget()
                        _widget.updated.connect(self.updated.emit)
                        _widget.set_namespace(_namespace)
                        _widget.load_project_entity(_asset)
                        _asset_widget[_asset_key] = _widget
                        self.add_widget(_widget)
                        self._project_entity_widgets.append(_widget)
                    _widget = _asset_widget[_asset_key]
                    
                    # for _input_task in _input_tasks
                    # if _input_task.get("ProjectEntityType") == "asset" and _input_task.get("ProjectEntityId") == _asset_id:
                    #     _widget.add_task_output_attr( _input_task.get("Id"),  _attr.id())

                    if _input_task.get("NameSpace") == _namespace:
                        _widget.add_task_output_attr( _input_task.get("Id"),  _attr.id(), _conn_attr.get("AttrInputId"))



class AssemblyWidget(RelyWidget):
    def __init__(self, parent = None):

        self._title = "assembly"

        super(AssemblyWidget, self).__init__(parent)

        # self._build()

    def load_task_id(self, task_id):
        _attrs = super(AssemblyWidget, self).load_task_id(task_id)
        self.title_button.setText(language.word(self._title))

        _task = zfused_api.task.Task(task_id)   
        _project_entity = _task.project_entity()
        # get relative asset
        _relative_assemblys = zfused_api.zFused.get("relative", filter = { "SourceObject": "assembly", "TargetObject": _project_entity.object(), "TargetId": _project_entity.id() })
        if not _relative_assemblys:
            return
        # _assembly_ids = [ _relative_assembly.get("SourceId") for _relative_assembly in _relative_assemblys ]
        if _attrs:
            for _attr in _attrs:
                _conn_attr = zfused_api.zFused.get("attr_conn", filter = {"AttrInputId": _attr.id()})
                if _conn_attr:
                    _conn_attr = _conn_attr[0]
                    _attr = zfused_api.attr.Output(_conn_attr.get("AttrOutputId"))

                    for _relative_assembly in _relative_assemblys:
                        _assembly_id = _relative_assembly.get("SourceId")
                        _namespace = _relative_assembly.get("NameSpace")
                        _assembly = zfused_api.assembly.Assembly(_assembly_id)
                        # _tasks = _assembly.tasks([_attr.project_step_id()])
                        # if _tasks:
                        #     _widget = TaskAttrWidget()
                        #     _widget.load(_tasks[0].get("Id"), _attr.id())
                        #     self.add_widget(_widget)
                        _widget = project_entity_widget.ProjectEntityWidget()
                        _widget.updated.connect(self.updated.emit)
                        _widget.set_namespace(_namespace)
                        _widget.load_project_entity(_assembly)
                        _widget.add_output_attr_id(_attr.id(), _conn_attr.get("AttrInputId"))
                        self.add_widget(_widget)
                        self._project_entity_widgets.append(_widget)
