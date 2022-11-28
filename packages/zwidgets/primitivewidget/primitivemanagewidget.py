# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import button,panel

from .any_widget import any_widget
from .inside_widget import inside_widget


__all__ = ["PrimitiveManageWidget"]

logger = logging.getLogger(__name__)


class PrimitiveManageWidget(panel.ShowPanelWidget):
    gpu_import = QtCore.Signal(str)
    inside_refreshed = QtCore.Signal()
    inside_project_step_changed = QtCore.Signal(int)
    selected = QtCore.Signal(list)
    switch_version = QtCore.Signal(bool)
    optimized = QtCore.Signal()
    def __init__(self, parent = None):
        super(PrimitiveManageWidget, self).__init__(parent)
        self._build()

        self._project_id = 0

        self.any_widget.gpu_import.connect(self.gpu_import.emit)

        self.inside_widget.gpu_import.connect(self.gpu_import.emit)
        self.inside_widget.inside_refreshed.connect(self.inside_refreshed.emit)
        self.inside_widget.inside_project_step_changed.connect(self.inside_project_step_changed.emit)
        self.inside_widget.selected.connect(self.selected.emit)
        self.inside_widget.switch_version.connect(self.switch_version.emit)
        self.inside_widget.optimized.connect(self.optimized.emit)

    def load_project_id(self, project_id):
        self._project_id = project_id
        self.any_widget.load_project_id(project_id)

    def load_elements(self, elements):
        self.inside_widget.load_elements(elements)
        
    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        # self.operation_widget = QtWidgets.QFrame()
        # _layout.addWidget(self.operation_widget)
        # self.operation_layout = QtWidgets.QHBoxLayout(self.operation_widget)

        self.tab_widget = QtWidgets.QTabWidget()
        _layout.addWidget(self.tab_widget)
        self.tab_widget.setStyleSheet("QTabWidget::tab-bar{subcontrol-position: center bottom;width:240px;}")

        self.any_widget = any_widget.AnyWidget()
        # _layout.addWidget(self.any_widget)
        self.tab_widget.addTab(self.any_widget, u"所有元素")

        self.inside_widget = inside_widget.InsideWidget()
        self.tab_widget.addTab(self.inside_widget, u"当前场景元素")


