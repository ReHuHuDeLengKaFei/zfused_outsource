# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

from zcore import resource


class ErrorPublishWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(ErrorPublishWidget, self).__init__(parent)
        self._build()

    def set_error_info(self, info):
        self.no_active_message_button.setText(info)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(5)
        _layout.setContentsMargins(0,0,0,0)

        self.no_active_widget = QtWidgets.QFrame()
        _layout.addWidget(self.no_active_widget)
        self.no_active_layout = QtWidgets.QVBoxLayout(self.no_active_widget)
        self.no_active_message_button = QtWidgets.QPushButton(self)
        self.no_active_message_button.setIcon(QtGui.QIcon(resource.get("icons","none.png")))
        self.no_active_message_button.setObjectName("no_active_message_button")
        self.no_active_message_button.setText(u"当前任务状态没有激活，无法发布上传")
        self.no_active_layout.addStretch(True)
        self.no_active_layout.addWidget(self.no_active_message_button)
        self.no_active_layout.addStretch(True)