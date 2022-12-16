# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import button

# from . import taskpanelwidget

from .element_listwidget import element_listwidget

# from zwidgets.filter_widget import project_step_filter_widget

# from . import operation_widget
from . import filter_widget

logger = logging.getLogger(__name__)


class InsideWidget(QtWidgets.QFrame):
    gpu_import = QtCore.Signal(str)
    
    inside_refreshed = QtCore.Signal()
    inside_project_step_changed = QtCore.Signal(int)

    selected = QtCore.Signal(list)
    switch_version = QtCore.Signal(bool)

    optimized = QtCore.Signal()

    def __init__(self, parent = None):
        super(InsideWidget, self).__init__(parent)
        self._build()

        self._project_id = 0

        self.refresh_button.clicked.connect(self.inside_refreshed.emit)

        # self.project_step_filter_widget.project_steps_changed.connect(self._filter_project_steps)

        self.element_listwidget.gpu_import.connect(self.gpu_import.emit)

        self.filter_widget.switch_step.connect(self.inside_project_step_changed.emit)

        self.filter_widget.selected.connect(self.selected.emit)
        self.filter_widget.switch_version.connect(self.switch_version.emit)

        self.filter_widget.optimized.connect(self.optimized.emit)

    def _refresh(self):
        self.element_listwidget.load_datas()

    def load_elements(self, elements):
        self._elements = elements
        self.element_listwidget.load_elements(elements)
        _project_step_ids = list(set([_element.get("project_step_id") for _element in elements]))
        # self.project_step_filter_widget.load_project_step_ids(_project_step_ids)
        # self._filter_project_steps([])

        self.filter_widget.load_elements(elements)

    def _filter_project_steps(self, project_step_ids):
        self.element_listwidget.task_proxy_model.filter_project_steps(project_step_ids)

    def showEvent(self, event):
        self.inside_refreshed.emit()
        super(InsideWidget, self).showEvent(event)

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
        
        self.title_layout.addStretch(True)
        self.prompt_label = QtWidgets.QLabel("右击选择切换版本")
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

        # self.filter_widget = QtWidgets.QFrame(self.splitter)
        # self.filter_widget.setMaximumWidth(300)
        # self.filter_layout = QtWidgets.QVBoxLayout(self.filter_widget)
        # self.filter_layout.setSpacing(0)
        # self.filter_layout.setContentsMargins(0,0,0,0)

        # self.project_step_filter_widget = project_step_filter_widget.ProjectStepFilterWidget(self)
        # self.filter_layout.addWidget(self.project_step_filter_widget)
        # self.filter_layout.addStretch(True)


        self.element_listwidget = element_listwidget.ElementListWidget(self.splitter)

        # self.operating_widget = operation_widget.OperationWidget()
        # _layout.addWidget(self.operating_widget)
        self.filter_widget = filter_widget.FilterWidget(self.splitter)

        self.splitter.setSizes([ 2/3.0*self.width(), 1/3.0*self.width() ])