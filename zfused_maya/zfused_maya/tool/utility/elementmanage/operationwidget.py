# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

import zfused_maya.core.record as record

__all__ = ["OperationWidget"]

logger = logging.getLogger(__name__)


class OperationWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(OperationWidget, self).__init__()
        self._build()

    def _build(self):
        """ build operation widget

        """
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        # update all 
        self.update_all_button = QtWidgets.QPushButton()
        self.update_all_button.setMinimumSize(100, 40)
        self.update_all_button.setText(u"更新至最新")
        _layout.addWidget(self.update_all_button)

        _layout.addStretch(True)