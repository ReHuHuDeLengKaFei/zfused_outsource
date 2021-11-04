# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

import zfused_maya.core.record as record

from zfused_maya.ui.widgets import window

import zfused_maya.node.core.element as element

from . import operationwidget
from . import elementlistwidget
from . import filterwidget

__all__ = ["ElementManageWidget"]

logger = logging.getLogger(__name__)


class ElementManageWidget(window._Window):
    def __init__(self, parent = None):
        super(ElementManageWidget, self).__init__(parent)
        self._build()
        self.operation_widget.update_all_button.clicked.connect(self._update_all)
        self.filter_widget._step_changed.connect(self._filter_step)


    def _filter_step(self, project_step_id):
        # interface
        _interface = record.Interface()
        _interface.write("element_manage_project_step_id", project_step_id)

        self._project_step_id = project_step_id
        self.scene_listwidget.item_delegate.replace_project_step_id = project_step_id
        self.scene_listwidget.list_view.repaint()

    def showEvent(self, event):
        super(ElementManageWidget, self).showEvent(event)
        self.load_config()

    def load_config(self):
        self.filter_widget.load_config()
        self.scene_listwidget.refresh_scene()

    def _update_all(self):
        """ update all elements
        """
        # 测试
        _elements = element.scene_elements()
        if not _elements:
            return
        for _element in _elements:
            _element_cls = element.ReferenceElement(_element)
            _element_cls.update()
        # # relatives
        # relatives.create_relatives()

    def _build(self):
        self.resize(1200, 800)
        self.set_title_name(u"元素管理(element management)")
        
        # self.current_task_widget = currenttaskwidget.CurrentTaskWidget()
        # self.set_central_widget(self.current_task_widget)

        # content widget
        self.content_widget = QtWidgets.QFrame()
        self.set_central_widget(self.content_widget)
        self.content_layout = QtWidgets.QHBoxLayout(self.content_widget)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0,0,0,0)

        self.splitter = QtWidgets.QSplitter()
        self.content_layout.addWidget(self.splitter)
        # filter widget
        self.filter_widget = filterwidget.FilterWidget(self.splitter)
        # scene listwidget
        self.scene_listwidget = elementlistwidget.ElementListWidget(self.splitter)
        
        # operation widget
        self.operation_widget = operationwidget.OperationWidget() 
        self.set_tail_widget(self.operation_widget)
