# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

from zcore import resource

from . import taskreceivewidget
from . import taskpublishwidget
from . import work_widget
from . import taskupdatewidget

# from . import taskassemblywidget

__all__ = ["OperationWidget"]

logger = logging.getLogger(__name__)


class OperationWidget(QtWidgets.QFrame):
    received = QtCore.Signal(str, int, list)
    published = QtCore.Signal(int, dict, dict)

    opened = QtCore.Signal(str)
    def __init__(self, parent = None):
        super(OperationWidget, self).__init__(parent)
        self._build()

        self._task_id = 0

        self.task_receive_widget.received.connect(self.received.emit)
        self.task_publish_widget.published.connect(self.published.emit)
        self.work_widget.opened.connect(self.opened.emit)
        self.task_update_widget.received.connect(self.received.emit)
        
        self.operation_tabwidget.currentChanged.connect(self._change)

    def _change(self, index):
        _widget = self.operation_tabwidget.widget(index)
        _widget.load_task_id(self._task_id)

    def load_task_id(self, task_id):
        """ load task id
        :rtype: None
        """
        self._task_id = task_id

        _widget = self.operation_tabwidget.currentWidget()
        _widget.load_task_id(self._task_id)

        # self.task_receive_widget.load_task_id(task_id)
        # self.task_publish_widget.load_task_id(task_id)
        # # self.task_assembly_widget.load_task_id(task_id)
        # self.work_widget.load_task_id(task_id)
    
    def load_assets(self, assets):
        self.task_publish_widget.load_assets(assets)

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

        self.task_receive_widget = taskreceivewidget.TaskReceiveWidget(self)
        self.operation_tabwidget.addTab(self.task_receive_widget, QtGui.QIcon(resource.get("icons","download.png")), u"下载文件")

        self.task_publish_widget = taskpublishwidget.TaskPublishWidget(self)
        self.operation_tabwidget.addTab(self.task_publish_widget, QtGui.QIcon(resource.get("icons","upload.png")), u"上传文件")

        self.work_widget = work_widget.WorkWidget()
        self.operation_tabwidget.addTab(self.work_widget, QtGui.QIcon(resource.get("icons", "file.png")), u"制作过程文件")

        self.task_update_widget = taskupdatewidget.TaskUpdateWidget()
        self.operation_tabwidget.addTab(self.task_update_widget, QtGui.QIcon(resource.get("icons", "refresh.png")), u"更新文件")

        # self.task_reference_widget = QtWidgets.QFrame()
        # self.operation_tabwidget.addTab(self.task_reference_widget, QtGui.QIcon(resource.get("icons","reference.png")), u"引用文件")

        # self.task_assembly_widget = taskassemblywidget.TaskAssemblyWidget(self)
        # self.operation_tabwidget.addTab(self.task_assembly_widget, QtGui.QIcon(resource.get("icons","assembly.png")), u"更新文件")

        _layout.addWidget(self.operation_tabwidget)