# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import lineedit

from . import iconitemdelegate,listview,listmodel


__all__ = ["AssemblyListWidget"]


class AssemblyListWidget(QtWidgets.QFrame):
    assembly_selected = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(AssemblyListWidget, self).__init__(parent)
        self._build()

        self.search_lineedit.search_clicked.connect(self._search)
        self.listwidget.doubleClicked.connect(self._selected_assembly)

    def _selected_assembly(self, index):
        _data = index.data()
        self.assembly_selected.emit(_data.get("Id"))

    def _search(self, text):
        """ search task
        """
        self.assembly_proxy_model.search(text)

    def load_project_id(self, project_id):
        """ 加载激活中任务
        """
        _assemblys = zfused_api.assembly.cache([project_id], False)
        _tasks = zfused_api.task.cache([project_id])
        self.assembly_model = listmodel.ListModel(_assemblys, self.listwidget)
        self.assembly_proxy_model.setSourceModel(self.assembly_model)
        # self.assembly_list_view.setModel(self.assembly_proxy_model)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

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
        self.assembly_proxy_model = listmodel.ListFilterProxyModel()
        self.listwidget.setModel(self.assembly_proxy_model)
        self.listwidget.setItemDelegate(iconitemdelegate.IconItemDelegate(self.listwidget))