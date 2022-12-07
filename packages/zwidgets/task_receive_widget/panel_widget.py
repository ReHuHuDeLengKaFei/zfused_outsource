# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import re

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource



class PanelWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(PanelWidget, self).__init__(parent)