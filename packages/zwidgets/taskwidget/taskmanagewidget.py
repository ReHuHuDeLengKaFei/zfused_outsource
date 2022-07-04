# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

from zwidgets.widgets import panel

from . import taskpanelwidget

from . import tasklistwidget
from . import filterwidget

__all__ = ["TaskManageWidget"]

logger = logging.getLogger(__name__)


class TaskManageWidget(panel.ShowPanelWidget):

    viewed = QtCore.Signal(int)
    checked = QtCore.Signal(int)

    def __init__(self, parent = None):
        super(TaskManageWidget, self).__init__(parent)
        self._build()
        self.build_panel()
        
        self.task_panel_widget = taskpanelwidget.TaskPanelWidget(self)
        self.load_panel_widget("task panel", self.task_panel_widget)

        self.task_listwidget.listwidget.doubleClicked.connect(self._show_panel)
        self.filter_widget._step_changed.connect(self._filter_step)

        self.task_listwidget.viewed.connect(self.viewed.emit)
        self.task_listwidget.checked.connect(self.checked.emit)

    def _show_panel(self, model_index):
        """ show panel 
        """
        _task_data = model_index.data()
        self.task_panel_widget.load_task_id(_task_data["Id"])
        self.show_panel()
        
    def load(self, project_id, company_id):
        self.task_listwidget.load(project_id, company_id)
        self.filter_widget.load_project_id(project_id)

    def _search(self):
        _text = self.search_line.text()
        self.asset_list_widget.asset_proxy_model.search(_text)

    def only_show_version(self):
        return self.verison_checkbox.isChecked()

    def _refresh_asset_step_panel(self):
        self.asset_step_widget.load_asset_id(self._asset_id)
        # load project step id
        self.asset_step_widget.load_project_step_id(self._project_step_id)

    def _load_task(self, index):
        _data = index.data()
        _task_id = _data["Id"]
        self.operation_widget.load_task(_task_id)

    def _filter_asset_types(self, type_ids = []):
        self.asset_list_widget.asset_proxy_model.filter_type(type_ids)

    def _filter_asset_project_steps(self, project_step_id):
        if self.only_show_version():
            self.asset_list_widget.asset_proxy_model.filter_project_steps([self._project_step_id])
        else:
            self.asset_list_widget.asset_proxy_model.filter_project_steps([])

    def _filter_step(self, project_step_id):
        # 可以重载函数 添加触发命令
        self._project_step_id = project_step_id
        self.task_listwidget.task_proxy_model.filter_project_steps([project_step_id])

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QtWidgets.QSplitter()
        _layout.addWidget(self.splitter)

        self.filter_widget = filterwidget.FilterWidget(self.splitter)

        self.task_listwidget = tasklistwidget.TaskListWidget(self.splitter)