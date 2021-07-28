# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource


from zwidgets.widgets import lineedit,button

from zwidgets.widgets import panel

from . import filterwidget
from . import assemblylistwidget
from . import assemblystepwidget

__all__ = ["AssemblyManageWidget"]

logger = logging.getLogger(__name__)


class AssemblyManageWidget(panel.ShowPanelWidget):
    reference_version = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(AssemblyManageWidget, self).__init__(parent)
        self._build()

        self.build_panel()
        self.assembly_step_widget = assemblystepwidget.AssemblyStepWidget()
        self.load_panel_widget("assembly panel", self.assembly_step_widget)

        self._project_id = 0
        self._assembly_id = 0
        self._project_step_id = 0

        self.filter_widget.assembly_type_changed.connect(self._filter_assembly_types)
        self.filter_widget.assembly_step_changed.connect(self._filter_assembly_steps)

        self.assembly_list_widget.assembly_selected.connect(self._load_assembly)
        
        self.verison_checkbox.stateChanged.connect(self._filter_assembly_project_steps)
        self.refresh_button.clicked.connect(self._reload)

        self.assembly_step_widget.reference_version.connect(self.reference_version.emit)

    def _reload(self):
        self.load_project_id(self._project_id)

    def load_project_id(self, project_id):
        self._project_id = project_id
        self.assembly_list_widget.load_project_id(project_id)
        self.filter_widget.load_project_id(project_id)

    def _search(self):
        # get search text
        _text = self.search_line.text()
        self.assembly_list_widget.assembly_proxy_model.search(_text)

    def only_show_version(self):
        return self.verison_checkbox.isChecked()

    def _refresh_assembly_step_panel(self):
        self.assembly_step_widget.load_assembly_id(self._assembly_id)
        # load project step id
        self.assembly_step_widget.load_project_step_id(self._project_step_id)
        self.show_panel()

    def _load_assembly(self, assembly_id):
        _assembly_id = assembly_id
        _assembly = zfused_api.assembly.Assembly(_assembly_id)
        _status_handle = _assembly.status()
        if not _status_handle.data()["IsFreeze"]:
            self._assembly_id = _assembly_id
        else:
            self._assembly_id = 0
        self._refresh_assembly_step_panel()

    def _filter_assembly_types(self, type_ids = []):
        self.assembly_list_widget.assembly_proxy_model.filter_type(type_ids)

    def _filter_assembly_project_steps(self, project_step_id):
        if self.only_show_version():
            self.assembly_list_widget.assembly_proxy_model.filter_project_steps([self._project_step_id])
        else:
            self.assembly_list_widget.assembly_proxy_model.filter_project_steps([])

    def _filter_assembly_steps(self, project_step_id):
        # # interface
        # _interface = record.Interface()
        # _interface.write("assembly_manage_project_step_id", project_step_id)
        self._project_step_id = project_step_id
        # self._refresh_assembly_step_panel()
        if self.only_show_version():
            self.assembly_list_widget.assembly_proxy_model.filter_project_steps([project_step_id])
        else:
            self.assembly_list_widget.assembly_proxy_model.filter_project_steps([])

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)

        #  操作窗口
        self.operation_widget = QtWidgets.QFrame()
        _layout.addWidget(self.operation_widget)
        self.operation_widget.setFixedHeight(30)
        self.operation_widget.setObjectName("operation_widget")
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_widget)
        self.operation_layout.setContentsMargins(0, 0, 0, 0)
        # show verison
        self.verison_checkbox = QtWidgets.QCheckBox()
        self.verison_checkbox.setText("只显示带有版本的")
        self.verison_checkbox.setChecked(True)
        self.operation_layout.addWidget(self.verison_checkbox)
        self.operation_layout.addStretch(True)
        # refresh button
        self.refresh_button = button.IconButton( self, 
                                                 resource.get("icons","refresh.png"),
                                                 resource.get("icons","refresh_hover.png"),
                                                 resource.get("icons","refresh_pressed.png") )
        self.refresh_button.setFixedSize(60, 24)
        self.refresh_button.setText(u"刷新")
        self.operation_layout.addWidget(self.refresh_button)

        # 分割窗口
        self.splitter = QtWidgets.QSplitter()
        _layout.addWidget(self.splitter)
        # 过滤面板
        self.filter_widget = filterwidget.FilterWidget(self.splitter)
        self.filter_widget.setMaximumWidth(200)
        # 资产列表面板
        self.assembly_list_widget = assemblylistwidget.AssemblyListWidget(self.splitter)
        