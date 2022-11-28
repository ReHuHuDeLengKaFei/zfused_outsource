# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import panel,button

# from . import taskpanelwidget

from . import primitivelistwidget
from . import filterwidget
from . import operationwidget

__all__ = ["PrimitiveManageWidget"]

logger = logging.getLogger(__name__)


class PrimitiveManageWidget(panel.ShowPanelWidget):
    gpu_import = QtCore.Signal(str)
    def __init__(self, parent = None):
        super(PrimitiveManageWidget, self).__init__(parent)
        self._build()

        self._project_id = 0

        # self.build_panel()
        # self.task_panel_widget = taskpanelwidget.TaskPanelWidget()
        # self.load_panel_widget("task panel", self.task_panel_widget)

        self.filter_widget.asset_type_changed.connect(self._filter_asset_types)
        self.filter_widget.asset_step_changed.connect(self._filter_asset_project_steps)

        self.primitive_listwidget.task_selected.connect(self._task_selected)

        self.refresh_button.clicked.connect(self._refresh)
        self.version_checkbox.stateChanged.connect(self._refresh)

        self.operating_widget.gpu_import.connect(self.gpu_import.emit)
        self.primitive_listwidget.gpu_import.connect(self.gpu_import.emit)

    def _refresh(self):
        self.primitive_listwidget.load_project_id(self._project_id, self.only_show_version())
        #　self.filter_widget.load_project_id(project_id)

    def _task_selected(self, task_id):
        _task = zfused_api.task.Task(task_id)
        self.operating_widget.load_task_id(task_id)

    # def _show_panel(self, model_index):
    #     """ show panel 
    #     """
    #     _task_data = model_index.data()
    #     self.task_panel_widget.load_task_id(_task_data["Id"])
    #     self.show_panel()
        
    def load_project_id(self, project_id):
        self._project_id = project_id
        self.primitive_listwidget.load_project_id(project_id, self.only_show_version())
        self.filter_widget.load_project_id(project_id)

    def _search(self):
        _text = self.search_line.text()
        self.primitive_listwidget.task_proxy_model.search(_text)

    def only_show_version(self):
        return self.version_checkbox.isChecked()

    # def _refresh_asset_step_panel(self):
    #     self.asset_step_widget.load_asset_id(self._asset_id)
    #     # load project step id
    #     self.asset_step_widget.load_project_step_id(self._project_step_id)

    def _load_task(self, index):
        _data = index.data()
        _task_id = _data["Id"]
        self.operation_widget.load_task(_task_id)

    def _filter_asset_types(self, type_ids = []):
        self.primitive_listwidget.task_proxy_model.filter_type(type_ids)

    def _filter_asset_project_steps(self, project_step_id):
        """
        """
        # if self.only_show_version():
        #     self.primitive_listwidget.task_proxy_model.filter_project_steps([self._project_step_id])
        # else:
        #     self.primitive_listwidget.task_proxy_model.filter_project_steps([])

        self.primitive_listwidget.task_proxy_model.filter_project_steps([project_step_id])

    def _filter_step(self, project_step_id):
        self._project_step_id = project_step_id
        self.primitive_listwidget.task_proxy_model.filter_project_steps([project_step_id])

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        self.title_widget = QtWidgets.QFrame()
        _layout.addWidget(self.title_widget)
        self.title_widget.setFixedHeight(30)
        self.title_widget.setObjectName("operation_widget")
        self.title_layout = QtWidgets.QHBoxLayout(self.title_widget)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        # show verison
        self.version_checkbox = QtWidgets.QCheckBox()
        self.version_checkbox.setText("只显示带有版本的")
        self.version_checkbox.setChecked(True)
        self.title_layout.addWidget(self.version_checkbox)
        self.title_layout.addStretch(True)
        self.prompt_label = QtWidgets.QLabel("新增右击选择下载")
        self.title_layout.addWidget(self.prompt_label)
        self.title_layout.addStretch(True)
        # refresh button
        self.refresh_button = button.IconButton( self, 
                                                 resource.get("icons","refresh.png"),
                                                 resource.get("icons","refresh_hover.png"),
                                                 resource.get("icons","refresh_pressed.png") )
        self.refresh_button.setFixedSize(60, 24)
        self.refresh_button.setText(u"刷新")
        self.title_layout.addWidget(self.refresh_button)

        self.splitter = QtWidgets.QSplitter()
        _layout.addWidget(self.splitter)

        self.filter_widget = filterwidget.FilterWidget(self.splitter)

        self.primitive_listwidget = primitivelistwidget.PrimitiveListWidget(self.splitter)

        self.operating_widget = operationwidget.OperationWidget()
        _layout.addWidget(self.operating_widget)