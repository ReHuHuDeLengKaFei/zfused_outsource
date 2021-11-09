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
from . import assetlistwidget
from . import assetstepwidget

__all__ = ["AssetManageWidget"]

logger = logging.getLogger(__name__)


class AssetManageWidget(panel.ShowPanelWidget):
    reference_by_attr = QtCore.Signal(int, int)
    def __init__(self, parent = None):
        super(AssetManageWidget, self).__init__(parent)
        self._build()

        self.build_panel()
        self.asset_step_widget = assetstepwidget.AssetStepWidget()
        self.load_panel_widget("asset panel", self.asset_step_widget)

        self._project_id = 0
        self._asset_id = 0
        self._project_step_id = 0

        self.filter_widget.asset_type_changed.connect(self._filter_asset_types)
        self.filter_widget.asset_step_changed.connect(self._filter_asset_steps)

        self.asset_list_widget.asset_selected.connect(self._load_asset)
        
        self.verison_checkbox.stateChanged.connect(self._filter_asset_project_steps)
        self.refresh_button.clicked.connect(self._reload)

        self.asset_step_widget.reference_by_attr.connect(self.reference_by_attr.emit)

    def _reload(self):
        self.load_project_id(self._project_id)

    def load_project_id(self, project_id):
        self._project_id = project_id
        self.asset_list_widget.load_project_id(project_id)
        self.filter_widget.load_project_id(project_id)

    def _search(self):
        # get search text
        _text = self.search_line.text()
        self.asset_list_widget.asset_proxy_model.search(_text)

    def only_show_version(self):
        return self.verison_checkbox.isChecked()

    def _refresh_asset_step_panel(self):
        self.asset_step_widget.load_asset_id(self._asset_id)
        # load project step id
        self.asset_step_widget.load_project_step_id(self._project_step_id)
        self.show_panel()

    def _load_asset(self, asset_id):
        _asset_id = asset_id
        _asset = zfused_api.asset.Asset(_asset_id)
        _status_handle = _asset.status()
        if not _status_handle.data()["IsFreeze"]:
            self._asset_id = _asset_id
        else:
            self._asset_id = 0
        self._refresh_asset_step_panel()

    def _filter_asset_types(self, type_ids = []):
        self.asset_list_widget.asset_proxy_model.filter_type(type_ids)

    def _filter_asset_project_steps(self, project_step_id):
        if self.only_show_version():
            self.asset_list_widget.asset_proxy_model.filter_project_steps([self._project_step_id])
        else:
            self.asset_list_widget.asset_proxy_model.filter_project_steps([])

    def _filter_asset_steps(self, project_step_id):
        # # interface
        # _interface = record.Interface()
        # _interface.write("asset_manage_project_step_id", project_step_id)
        self._project_step_id = project_step_id
        # self._refresh_asset_step_panel()
        if self.only_show_version():
            self.asset_list_widget.asset_proxy_model.filter_project_steps([project_step_id])
        else:
            self.asset_list_widget.asset_proxy_model.filter_project_steps([])

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
        self.filter_widget.setMaximumWidth(250)
        # 资产列表面板
        self.asset_list_widget = assetlistwidget.AssetListWidget(self.splitter)
        