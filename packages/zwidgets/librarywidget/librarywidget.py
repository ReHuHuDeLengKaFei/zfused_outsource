# coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from ..widgets import panel

import entitylistwidget
import librarylistwidget
import previewwidget
import categorywidget
import entitywidget

__all__ = ["LibraryWidget"]

logger = logging.getLogger(__name__)


class LibraryWidget(panel.ShowPanelWidget):
    def __init__(self, parent = None):
        super(LibraryWidget, self).__init__(parent)
        self._build()
        self.build_panel()

        self._library_id = 0

        self.entity_widget = entitywidget.EntityWidget(self)
        self.load_panel_widget("library entity", self.entity_widget)

        self.library_listwidget.library_selected.connect(self._change_library)
        self.entity_listwidget.entity_selected.connect(self._show_entity)

    def _show_entity(self, entity_id):
        self.show_panel()
        self.entity_widget.load_entity(entity_id)

    def _change_library(self, library_id):
        if self._library_id == library_id:
            return
        self._library_id = library_id
        self.preview_widget.load_library(library_id)
        self.category_widget.load_library(library_id)
        self.entity_listwidget.load_library(library_id)

    def load_config(self):
        """ load default
        """ 
        self.library_listwidget.load_config()

    def resizeEvent(self, event):
        self.library_listwidget.setMinimumWidth(self.width()*0.1)
        self.library_listwidget.setMaximumWidth(self.width()*0.2)
        super(LibraryWidget, self).resizeEvent(event)

    def _build(self):
        """ build widget
        """
        self.resize(1200, 800)
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        self.splitter = QtWidgets.QSplitter()
        _layout.addWidget(self.splitter)

        # library listwidget
        self.library_listwidget = librarylistwidget.LibraryListWidget(self.splitter)

        # entity listwidget
        self.entity_contant_widget = QtWidgets.QFrame(self.splitter)
        self.entity_contant_layout = QtWidgets.QVBoxLayout(self.entity_contant_widget)
        self.entity_contant_layout.setSpacing(0)
        self.entity_contant_layout.setContentsMargins(0,0,0,0)
        # 添加预览
        self.preview_widget = previewwidget.PreviewWidget()
        self.entity_contant_layout.addWidget(self.preview_widget)
        # 分类
        self.category_widget = categorywidget.CategoryWidget()
        self.entity_contant_layout.addWidget(self.category_widget)
        # 
        self.entity_listwidget = entitylistwidget.EntityListWidget()
        self.entity_contant_layout.addWidget(self.entity_listwidget)