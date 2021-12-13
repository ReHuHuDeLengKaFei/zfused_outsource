# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import lineedit

from . import iconitemdelegate,listview,listmodel


__all__ = ["AssetListWidget"]


class AssetListWidget(QtWidgets.QFrame):
    asset_selected = QtCore.Signal(int)
    referenced = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(AssetListWidget, self).__init__(parent)
        self._build()

        self.search_lineedit.search_clicked.connect(self._search)

        self.listwidget.referenced.connect(self.referenced.emit)
        self.listwidget.doubleClicked.connect(self._selected_asset)

    def _selected_asset(self, index):
        _data = index.data()
        self.asset_selected.emit(_data.get("Id"))

    def _search(self, text):
        """ search task
        """
        self.asset_proxy_model.search(text)

    @zfused_api.reset
    def load_project_id(self, project_id, company_id = 0):
        """ 加载激活中任务
        """
        _assets = zfused_api.asset.cache([project_id], False)
        self.asset_model = listmodel.ListModel(_assets, self.listwidget)
        self.asset_proxy_model.setSourceModel(self.asset_model)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(2,2,2,2)
        _layout.setSpacing(2)

        self.contant_widget = QtWidgets.QFrame()
        _layout.addWidget(self.contant_widget)
        self.contant_layout = QtWidgets.QVBoxLayout(self.contant_widget)
        self.contant_layout.setContentsMargins(0,0,0,0)
        self.contant_layout.setSpacing(0)
        self.setObjectName("widget")

        # search name
        self.search_lineedit = lineedit.SearchLineEdit()
        self.contant_layout.addWidget(self.search_lineedit)
        self.search_lineedit.setMinimumHeight(24)

        # task list widget
        self.listwidget = listview.ListView()
        self.listwidget.setViewMode(QtWidgets.QListView.IconMode)
        self.contant_layout.addWidget(self.listwidget)
        self.listwidget.setObjectName("listwidget")
        self.asset_proxy_model = listmodel.ListFilterProxyModel()
        self.listwidget.setModel(self.asset_proxy_model)
        self.listwidget.setItemDelegate(iconitemdelegate.IconItemDelegate(self.listwidget))