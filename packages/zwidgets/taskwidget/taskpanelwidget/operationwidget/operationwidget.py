# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

from zcore import resource

from . import taskreceivewidget
from . import taskpublishwidget

__all__ = ["OperationWidget"]

logger = logging.getLogger(__name__)


class OperationWidget(QtWidgets.QFrame):
    received = QtCore.Signal(str, int)
    published = QtCore.Signal(str, int, dict)
    def __init__(self, parent = None):
        super(OperationWidget, self).__init__(parent)
        self._build()

        self.task_receive_widget.received.connect(self.received.emit)
        self.task_publish_widget.published.connect(self.published.emit)

    def load_task_id(self, task_id):
        """ load task id

        :rtype: None
        """
        self.task_receive_widget.load_task_id(task_id)
        self.task_publish_widget.load_task_id(task_id)

    def set_locked(self, is_lock):
        self.task_publish_widget.setEnabled(is_lock)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(0,0,0,0)

        # operation name button
        self.operation_name_button = QtWidgets.QPushButton()
        self.operation_name_button.setObjectName("operation_name_button")
        self.operation_name_button.setMinimumHeight(25)
        self.operation_name_button.setText(u"操作列表")
        self.operation_name_button.setIcon(QtGui.QIcon(resource.get("icons", "tabwidget.png")))

        # operation tabwidget
        self.operation_tabwidget = QtWidgets.QTabWidget()
        self.operation_tabwidget = QtWidgets.QTabWidget()
        self.operation_tabwidget.setIconSize(QtCore.QSize(20,20))

        self.task_receive_widget = taskreceivewidget.TaskReceiveWidget(self)
        self.operation_tabwidget.addTab(self.task_receive_widget, QtGui.QIcon(resource.get("icons","receive.png")), u"领取文件")

        self.task_publish_widget = taskpublishwidget.TaskPublishWidget(self)
        self.operation_tabwidget.addTab(self.task_publish_widget, QtGui.QIcon(resource.get("icons","publish.png")), u"上传文件")

        _layout.addWidget(self.operation_tabwidget)