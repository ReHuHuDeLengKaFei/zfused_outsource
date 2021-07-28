# coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import lineedit,button

__all__ = ["ThumbnailWidget"]

logger = logging.getLogger(__name__)


class ThumbnailWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(ThumbnailWidget, self).__init__(parent)
        self._build()

        self._entity_id = 0
        self._entity_handle = None

    def load_entity(self, entity_id):
        if self._entity_id == entity_id:
            return
        self._entity_id = entity_id
        self._entity_handle = zfused_api.library.LibraryEntity(entity_id)
        _library_handle = zfused_api.library.Library(self._entity_handle.data().get("LibraryId"))
        self.thumbnail_widget.setStyleSheet("QFrame{background-color:%s}"%(_library_handle.color()))
        self.thumbnail_button.set_thumbnail(self._entity_handle.get_thumbnail())
        self.name_button.setText(self._entity_handle.name())
        self.code_button.setText(self._entity_handle.code())

    def _build(self):
        """ build widget
        """
        self._zoom = 1.4
        self.setFixedHeight(108*self._zoom + 20)
        
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # thumbnail layout
        self.thumbnail_widget = QtWidgets.QFrame()
        
        _layout.addWidget(self.thumbnail_widget)
        self.thumbnail_layout = QtWidgets.QHBoxLayout(self.thumbnail_widget)
        self.thumbnail_layout.setSpacing(2)
        self.thumbnail_layout.setContentsMargins(10,10,10,10)
        self.thumbnail_button = button.ThumbnailButton(None, self)
        self.thumbnail_button.setFixedSize(192*self._zoom, 108*self._zoom)
        self.thumbnail_layout.addWidget(self.thumbnail_button)
        # H
        self.name_widget = QtWidgets.QWidget()
        self.thumbnail_layout.addWidget(self.name_widget)
        self.name_layout = QtWidgets.QVBoxLayout(self.name_widget)
        self.name_layout.setSpacing(8)
        self.name_layout.setContentsMargins(2,2,2,2)
        self.name_button = QtWidgets.QPushButton()
        self.name_button.setStyleSheet("QPushButton{font: 16pt bold;background-color: rgba(255, 255, 255, 0);color: rgb(255, 255, 255);Text-align: left;}")
        self.name_layout.addWidget(self.name_button)
        self.code_button = QtWidgets.QPushButton()
        self.code_button.setStyleSheet("QPushButton{font: 12pt bold;background-color: rgba(255, 255, 255, 0);color: rgb(218, 218, 218);Text-align: left;}")
        self.name_layout.addWidget(self.code_button)
        self.name_layout.addStretch(True)
