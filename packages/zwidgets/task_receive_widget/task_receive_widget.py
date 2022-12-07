# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import panel

from zwidgets.widgets import button

from . import task_listwidget
from . import filter_widget
from . import panel_widget
from . import version_listwidget

logger = logging.getLogger(__name__)


class TaskReceiveWidget(panel.ShowPanelWidget):

    viewed = QtCore.Signal(int)
    checked = QtCore.Signal(int)
    quick_downloaded = QtCore.Signal(int)
    quick_published = QtCore.Signal(int)

    def __init__(self, parent = None):
        super(TaskReceiveWidget, self).__init__(parent)
        self._build()
        self.build_panel()

        self._company_id = 0
        self._project_id = 0

        self.task_panel_widget = version_listwidget.VersionListWidget(self)
        self.load_panel_widget("task panel", self.task_panel_widget)

        self.task_listwidget.listwidget.doubleClicked.connect(self._show_panel)
        self.filter_widget._step_changed.connect(self._filter_step)

        self.verison_checkbox.stateChanged.connect(self._filter_need_update)

        self.task_listwidget.viewed.connect(self.viewed.emit)
        self.task_listwidget.checked.connect(self.checked.emit)
        self.task_listwidget.quick_downloaded.connect(self.quick_downloaded.emit)
        self.task_listwidget.quick_published.connect(self.quick_published.emit)

    def _show_panel(self, model_index):
        """ show panel 
        """
        _file_provide_data = model_index.data()
        self.task_panel_widget.load_task_id(_file_provide_data.get("TaskId"))
        self.show_panel()
        
    def load_project_id(self, project_id):
        self.task_listwidget.load_project_id(project_id)
        self.filter_widget.load_project_id(project_id)

    def _search(self):
        _text = self.search_line.text()
        self.asset_list_widget.asset_proxy_model.search(_text)

    def _filter_step(self, project_step_ids):
        self.task_listwidget.task_proxy_model.filter_project_steps(project_step_ids)

    def _filter_need_update(self, is_need):
        self.task_listwidget.task_proxy_model.filter_need_update(is_need)

    def refresh(self):
        self.load(self._company_id, self._project_id)

    def load(self, company_id, project_id):
        self._company_id = company_id
        self._project_id = project_id
        self.filter_widget.load_project_id(project_id)
        _file_provides = zfused_api.zFused.get("file_provide", filter = {"ProjectId": project_id, "CompanyId": company_id}, fields = ["Id"])
        if _file_provides:
            _file_provides = zfused_api.fileprovide.cache_from_ids([_file_provide.get("Id") for _file_provide in _file_provides])
        else:
            _file_provides = []
        self.task_listwidget.load_datas(_file_provides)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0, 0, 0, 0)

        #  操作窗口
        self.operation_widget = QtWidgets.QFrame()
        _layout.addWidget(self.operation_widget)
        self.operation_widget.setFixedHeight(30)
        self.operation_widget.setObjectName("operation_widget")
        self.operation_layout = QtWidgets.QHBoxLayout(self.operation_widget)
        self.operation_layout.setContentsMargins(0, 0, 0, 0)
        # show verison
        self.verison_checkbox = QtWidgets.QCheckBox()
        self.verison_checkbox.setText(u"只显示需要更新的")
        # self.verison_checkbox.setChecked(True)
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

        self.splitter = QtWidgets.QSplitter()
        _layout.addWidget(self.splitter)

        self.filter_widget = filter_widget.FilterWidget(self.splitter)

        self.task_listwidget = task_listwidget.TaskListWidget(self.splitter)