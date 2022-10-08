# coding:utf-8
# --author-- lanhua.zhou

""" 任务面板 """

from __future__ import print_function

from functools import partial
import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import button

logger = logging.getLogger(__name__)


class IndexWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(IndexWidget, self).__init__(parent)
        self._build()


    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0,0,0,0)

        # asset sequence shot
        self.tabwidget = QtWidgets.QTabWidget()
        _layout.addWidget(self.tabwidget)

        # asset index widget
        self.asset_widget = QtWidgets.QFrame()

        # sequence index widget
        self.sequence_widget = QtWidgets.QFrame()

        # shot index widget
        self.shot_widget = QtWidgets.QFrame()

        self.tabwidget.addTab(self.asset_widget, language.word("asset"))
        self.tabwidget.addTab(self.sequence_widget, language.word("sequence"))
        self.tabwidget.addTab(self.shot_widget, language.word("shot"))
