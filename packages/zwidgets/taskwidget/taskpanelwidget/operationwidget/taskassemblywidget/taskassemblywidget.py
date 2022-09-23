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


from . import projectentitywidget



class TaskAssemblyWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(TaskAssemblyWidget, self).__init__(parent)
        self._build()
        self._task_id = 0

    @zfused_api.reset
    def load_task_id(self, task_id):
        self._task_id = task_id

        self.self_widget.load_task_id(task_id)
        self.asset_widget.load_task_id(task_id)
        self.assembly_widget.load_task_id(task_id)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0,4,0,0)

        self.self_widget = SelfWidget()
        _layout.addWidget(self.self_widget)

        self.asset_widget = AssetWidget()
        _layout.addWidget(self.asset_widget)

        self.assembly_widget = AssemblyWidget()
        _layout.addWidget(self.assembly_widget)

        _layout.addStretch(True)



class RelyWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(RelyWidget, self).__init__(parent)
        self._title = "rely"

    def _set_contant_show(self, is_show):
        self.contant_widget.setHidden(not is_show)

    def load_task_id(self, task_id):
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
        _layout.setContentsMargins(2,2,2,2)

        self.title_widget = QtWidgets.QFrame()
        _layout.addWidget(self.title_widget)
        self.title_layout = QtWidgets.QHBoxLayout(self.title_widget)
        self.title_layout.setSpacing(2)
        self.title_layout.setContentsMargins(2,2,2,2)
        self.title_button = QtWidgets.QLabel()
        self.title_button.setText(self._title)
        # self.title_button.setObjectName("title_button")
        self.title_layout.addWidget(self.title_button)
        self.title_layout.addStretch(True)
        self.view_checkbox = QtWidgets.QCheckBox()
        self.view_checkbox.setChecked(True)
        self.view_checkbox.stateChanged.connect(self._set_contant_show)
        self.view_checkbox.setText(u"显示")
        self.title_layout.addWidget(self.view_checkbox)

        self.contant_widget = QtWidgets.QFrame()
        _layout.addWidget(self.contant_widget)
        self.contant_layout = QtWidgets.QVBoxLayout(self.contant_widget)
        self.contant_layout.setSpacing(4)
        self.contant_layout.setContentsMargins(4,4,4,4)



class SelfWidget(RelyWidget):
    def __init__(self, parent = None):
        super(SelfWidget, self).__init__(parent)

        self._title = "self"

        self._build()

    def load_task_id(self, task_id):
        _attrs = super(SelfWidget, self).load_task_id(task_id)
        _task = zfused_api.task.Task(task_id)       
        _project_entity = _task.project_entity()
        # self.title_button.setText(_project_entity.name_code())
        if _attrs:
            for _attr in _attrs:
                _conn_attr = zfused_api.zFused.get("attr_conn", filter = {"AttrInputId": _attr.get("Id")})
                if _conn_attr:
                    _conn_attr = _conn_attr[0]
                    _attr = zfused_api.attr.Output(_conn_attr.get("AttrOutputId"))
                    _tasks = _project_entity.tasks([_attr.project_step_id()])
                    if not _tasks:
                        continue
                    # if _tasks:
                    #     _widget = ProjectEntityWidget()
                    #     _widget.load(_tasks[0].get("Id"), _attr.id())
                    #     self.add_widget(_widget)
                    _task = _tasks[0]
                    _widget = projectentitywidget.ProjectEntityWidget()
                    _widget.load_project_entity(_project_entity)
                    # _widget.add_output_attr_id(_attr.id())
                    _widget.add_task_output_attr( _task.get("Id"),  _attr.id())
                    self.add_widget(_widget)




class AssetWidget(RelyWidget):
    def __init__(self, parent = None):
        super(AssetWidget, self).__init__(parent)

        self._title = "asset"

        self._build()

    def load_task_id(self, task_id):
        _attrs = super(AssetWidget, self).load_task_id(task_id)
        self.title_button.setText(language.word(self._title))

        _task = zfused_api.task.Task(task_id)   
        _project_entity = _task.project_entity()
        
        # get relative asset
        _relative_assets = zfused_api.zFused.get("relative", filter = { "SourceObject": "asset", "TargetObject": _project_entity.object(), "TargetId": _project_entity.id() })
        if not _relative_assets:
            return
        
        _asset_ids = [ _relative_asset.get("SourceId") for _relative_asset in _relative_assets ]
        _asset_widget = {}

        if not _attrs:
            return

        for _attr in _attrs:
            _conn_attr = zfused_api.zFused.get("attr_conn", filter = {"AttrInputId": _attr.get("Id")})
            if not _conn_attr:
                return

            _conn_attr = _conn_attr[0]
            _mode = _conn_attr.get("Mode")
            _attr = zfused_api.attr.Output(_conn_attr.get("AttrOutputId"))

            for _relative_asset in _relative_assets:
                _asset_id = _relative_asset.get("SourceId")
                _namespace = _relative_asset.get("NameSpace")
                _asset = zfused_api.asset.Asset(_asset_id)
                if _asset_id not in _asset_widget:
                    _widget = projectentitywidget.ProjectEntityWidget()
                    _widget.set_namespace(_namespace)
                    _widget.load_project_entity(_asset)
                    _asset_widget[_asset_id] = _widget
                    self.add_widget(_widget)
                _widget = _asset_widget[_asset_id]

                if _mode == "relative":
                    _tasks = _asset.tasks([_attr.project_step_id()])
                    if not _tasks:
                        continue
                    _task = _tasks[0]
                    _widget.add_task_output_attr( _task.get("Id"),  _attr.id())
                elif _mode == "direct":
                    _tasks = _project_entity.tasks([_attr.project_step_id()])
                    if not _tasks:
                        continue
                    _task = _tasks[0]
                    _widget.add_task_output_attr(_task.get("Id"),  _attr.id())



class AssemblyWidget(RelyWidget):
    def __init__(self, parent = None):
        super(AssemblyWidget, self).__init__(parent)

        self._title = "assembly"

        self._build()

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
                _conn_attr = zfused_api.zFused.get("attr_conn", filter = {"AttrInputId": _attr.get("Id")})
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
                        _widget = projectentitywidget.ProjectEntityWidget()
                        _widget.set_namespace(_namespace)
                        _widget.load_project_entity(_assembly)
                        _widget.add_output_attr_id(_attr.id())
                        self.add_widget(_widget)
