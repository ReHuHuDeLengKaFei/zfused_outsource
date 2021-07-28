# coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,zfile,transfer

from ..widgets import button


__all__ = ["PreviewWidget"]

logger = logging.getLogger(__name__)


class PreviewWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(PreviewWidget, self).__init__(parent)
        self._build()

        self._library_id = 0
        self._library_handle = None

    def load_library(self, library_id):
        if self._library_id == library_id:
            return
        self._library_id = library_id
        self._library_handle = zfused_api.library.Library(library_id)
        self.setStyleSheet("QFrame{background-color:%s}"%(self._library_handle.color()))
        self.thumbnail_button.set_thumbnail(self._library_handle.get_thumbnail())
        self.name_button.setText(self._library_handle.name())
        self.code_button.setText(self._library_handle.code())

    def _build(self):
        """ build widget
        """
        self.setFixedHeight(128)

        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(10,10,10,10)

        # thumbnail
        self.thumbnail_button = button.ThumbnailButton(None, self)
        self.thumbnail_button.setFixedSize(192, 108)
        _layout.addWidget(self.thumbnail_button)

        # 
        self.name_widget = QtWidgets.QWidget()
        _layout.addWidget(self.name_widget)
        self.name_layout = QtWidgets.QVBoxLayout(self.name_widget)
        self.name_layout.setSpacing(8)
        self.name_layout.setContentsMargins(2,2,2,2)
        self.name_button = QtWidgets.QPushButton()
        self.name_button.setStyleSheet("QPushButton{font: 16pt bold;background-color: rgba(255, 255, 255, 0);color: rgb(255, 255, 255);Text-align: left;border-radius: 0px;}")
        self.name_layout.addWidget(self.name_button)
        self.code_button = QtWidgets.QPushButton()
        self.code_button.setStyleSheet("QPushButton{font: 12pt bold;background-color: rgba(255, 255, 255, 0);color: rgb(218, 218, 218);Text-align: left;border-radius: 0px;}")
        self.name_layout.addWidget(self.code_button)
        self.name_layout.addStretch(True)
        # 
        _layout.addStretch(True)

        # self.progress_bar = QtWidgets.QProgressBar(self)
        # self.progress_bar.hide()
        # test
        # self.setStyleSheet("QFrame{background-color:#FFFFFF}")