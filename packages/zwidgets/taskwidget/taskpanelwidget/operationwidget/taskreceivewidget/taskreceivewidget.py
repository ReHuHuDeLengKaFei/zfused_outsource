# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,transfer

from . import versionwidget
from . import assemblywidget


logger = logging.getLogger(__name__)

__all__ = ["TaskReceiveWidget"]


class TaskReceiveWidget(QtWidgets.QFrame):
    received = QtCore.Signal(str, int)
    def __init__(self, parent = None):
        super(TaskReceiveWidget, self).__init__(parent)
        self._build()

        self._task_id = 0

        self.assembly_checkbox.stateChanged.connect(self._change_assembly)
        self.receive_button.clicked.connect(self._receive_file)
        #self._change_assembly()

    def load_task_id(self, task_id):
        """ load task id
        :rtype: None
        """
        if not task_id:
            return
        self._task_id = task_id
        self.version_widget.load_task_id(task_id)
        self.assembly_widget.load_task_id(task_id)

    def _receive_file(self):
        """ load sel index file
        :rtype: None
        """
        _is_assembly = self.is_assembly()
        if not _is_assembly:
            _index = self.version_widget.version_listwidget.currentIndex()
            if not _index:
                return
            self.received.emit("version", _index.data().get("Id"))
        else:
            self.received.emit("task", self._task_id)

    def is_assembly(self):
        """ is first receive

        :rtype: bool
        """
        return self.assembly_checkbox.isChecked()

    def _change_assembly(self, value):
        """ will assemblu file

        :rtype: None
        """
        if value:
            self.tab_widget.setCurrentIndex(1)
            self.title_button.setText(u"新合成文件")
        else:
            self.tab_widget.setCurrentIndex(0)
            self.title_button.setText(u"按版本领取文件")

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        self.title_button = QtWidgets.QPushButton()
        self.title_button.setMinimumHeight(25)
        self.title_button.setText(u"按版本领取文件")
        self.title_button.setObjectName("title_button")
        self.title_button.setIcon(QtGui.QIcon(resource.get("icons","download.png")))

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.tabBar().hide()
        # version widget
        self.version_widget = versionwidget.VersionWidget()
        self.tab_widget.addTab(self.version_widget, "version")
        # assembly widget
        self.assembly_widget = assemblywidget.AssemblyWidget()
        self.tab_widget.addTab(self.assembly_widget, "assembly")

        # receive widget
        self.receive_widget = QtWidgets.QFrame()
        self.receive_widget.setObjectName("receive_widget")
        self.receive_widget.setMinimumHeight(40)
        self.receive_layout = QtWidgets.QHBoxLayout(self.receive_widget)
        self.receive_layout.setSpacing(2)
        self.receive_layout.setContentsMargins(6,6,6,6)
        #  receive first checkbox
        self.assembly_checkbox = QtWidgets.QCheckBox()
        self.assembly_checkbox.setText(u"首次领取")
        self.assembly_checkbox.setToolTip(u"首次自动组装文件")
        self.receive_layout.addWidget(self.assembly_checkbox)
        self.receive_layout.addStretch(True)
        #  receive button
        self.receive_button = QtWidgets.QPushButton()
        self.receive_button.setMinimumHeight(30)
        self.receive_button.setObjectName("receive_button")
        self.receive_button.setMinimumWidth(80)
        self.receive_button.setIcon(QtGui.QIcon(resource.get("icons","receive.png")))
        self.receive_button.setText(u"领取文件")
        self.receive_layout.addWidget(self.receive_button)

        _layout.addWidget(self.title_button)
        _layout.addWidget(self.tab_widget)
        _layout.addWidget(self.receive_widget)