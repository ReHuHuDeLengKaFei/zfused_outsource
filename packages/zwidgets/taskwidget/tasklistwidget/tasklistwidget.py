# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import lineedit

from . import iconitemdelegate,listview,listmodel


__all__ = ["TaskListWidget"]


class TaskListWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(TaskListWidget, self).__init__(parent)
        self._build()
        self.search_lineedit.search_clicked.connect(self._search)

    def _search(self, text):
        """ search task
        """
        self.task_proxy_model.search(text)
        #self.setFocus()

    def load_project_id(self, project_id):
        """ 加载激活中任务

        """
        zfused_api.zFused.RESET = True
        # _user_id = zfused_api.zFused.USER_ID
        _current_project_id = project_id
        # _software_id = zfused_katana.software_id()
        _tasks = zfused_api.zFused.get("task", filter={"ProjectId": _current_project_id}, sortby = ["Name"], order = ["asc"])
        model = listmodel.ListModel(_tasks, self.listwidget)
        self.task_proxy_model.setSourceModel(model)
        zfused_api.zFused.RESET = False

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
        self.task_proxy_model = listmodel.ListFilterProxyModel()
        self.listwidget.setModel(self.task_proxy_model)
        self.listwidget.setItemDelegate(iconitemdelegate.IconItemDelegate(self.listwidget))