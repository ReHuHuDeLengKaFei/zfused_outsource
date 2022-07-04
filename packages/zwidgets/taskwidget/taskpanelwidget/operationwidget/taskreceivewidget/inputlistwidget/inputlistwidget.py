# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import lineedit,button

from . import inputlistview
from . import inputlistmodel
from . import inputitemdelegate

__all__ = ["InputListWidget"]

logger = logging.getLogger(__name__)


class InputListWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(InputListWidget, self).__init__(parent)
        self._build()
        
    def load_task_id(self, task_id):
        """ load task id

        """
        # reset api data ？
        zfused_api.zFused.RESET = True
        _task_handle = zfused_api.task.Task(task_id)
        _tasks = _task_handle.input_tasks()
        _task_list = []

        for _input_attr_id, _task in _tasks.items():
            _task_list.append(_input_attr_id)
            _task_list += _task

        _model = inputlistmodel.InputListModel(_task_list)
        self.input_proxy_model.setSourceModel(_model)
        zfused_api.zFused.RESET = False

    def _build(self):
        # build widget
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0,0,0,0)

        # search widget
        self.search_widget = QtWidgets.QFrame()
        self.search_widget.setMinimumHeight(25)
        self.search_layout = QtWidgets.QHBoxLayout(self.search_widget)
        self.search_layout.setSpacing(0)
        self.search_layout.setContentsMargins(0,0,0,0)
        #  search lineeit
        self.search_lineedit = lineedit.LineEdit()
        self.search_lineedit.setMinimumHeight(25)
        self.search_lineedit.set_tip(u"搜索")
        self.search_layout.addWidget(self.search_lineedit)
        #  search button
        self.search_button = button.IconButton( self.search_widget,
                                                resource.get("icons","refresh.png"),
                                                resource.get("icons","refresh.png"),
                                                resource.get("icons","refresh.png") )
        self.search_button.setMinimumSize(25,25)
        self.search_layout.addWidget(self.search_button)
        
        # input listwidget
        self.input_listwidget = inputlistview.InputListView()
        self.input_listwidget.setObjectName("input_listwidget")
        self.input_proxy_model = inputlistmodel.InputFilterProxyModel()
        self.input_listwidget.setModel(self.input_proxy_model)
        self.input_listwidget.setItemDelegate(inputitemdelegate.InputItemDelegate(self.input_listwidget))

        _layout.addWidget(self.search_widget)
        _layout.addWidget(self.input_listwidget)