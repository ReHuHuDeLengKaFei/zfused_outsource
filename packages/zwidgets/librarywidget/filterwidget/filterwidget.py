# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

__all__ = ["FilterWidget"]

logger = logging.getLogger(__name__)


class FilterWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(FilterWidget, self).__init__(parent)
        self._build()

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        # categroy

        # tag