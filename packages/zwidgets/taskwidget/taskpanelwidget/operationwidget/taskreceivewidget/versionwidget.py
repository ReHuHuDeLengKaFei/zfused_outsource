# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

# from .versionlistwidget import versionitemdelegate
# from .versionlistwidget import versionlistmodel
# from .versionlistwidget import versionlistview

from zwidgets.version_widget import version_listwidget

__all__ = ["VersionWidget"]


class VersionWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(VersionWidget, self).__init__(parent)
        self._build()

        self.version_listwidget.clicked.connect(self._show_description)

    def load_task_id(self, task_id):

        _task_handle = zfused_api.task.Task(task_id)
        _is_sub_task = _task_handle.is_sub_task()
        if _is_sub_task:
            _task_handle = zfused_api.task.Task(_task_handle.parent_task_id())
        
        _versions = _task_handle.versions(refresh = True)
        
        if not _versions:
            self.no_version_widget.setHidden(False)
            self.version_widget.setHidden(True)
            return

        self.no_version_widget.setHidden(True)
        self.version_widget.setHidden(False)        
        _versions.reverse()
        # _model = versionlistmodel.VersionListModel(_versions)
        # self.version_listwidget.setModel(_model)
        self.version_listwidget.load_versions(_versions)

    def _show_description(self, index):
        _message_text = index.data()["Description"]
        self.message_textedit.setText(_message_text)

    def index(self):
        return self.version_listwidget.index()

    def _build(self):
        # build widget
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # version widget
        self.version_widget = QtWidgets.QFrame()
        _layout.addWidget(self.version_widget)
        self.version_layout = QtWidgets.QVBoxLayout(self.version_widget)
        self.version_layout.setSpacing(0)
        self.version_layout.setContentsMargins(0,0,0,0)

        #  verison list widget
        # self.version_listwidget = versionlistview.VersionListView()
        # self.version_layout.addWidget(self.version_listwidget)
        # self.version_listwidget.setMouseTracking(True)
        # self.version_listwidget.setSpacing(2)
        # self.version_listwidget.setContentsMargins(2,2,2,2)
        # self.version_listwidget.setResizeMode(QtWidgets.QListView.Adjust)
        # self.version_listwidget.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        # self.version_listwidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.version_listwidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.version_listwidget.setItemDelegate(versionitemdelegate.VersionItemDelegate(self.version_listwidget))
        self.version_listwidget = version_listwidget.VersionListWidget()
        self.version_layout.addWidget(self.version_listwidget)

        # version infomation widget
        self.message_widget = QtWidgets.QFrame()
        self.version_layout.addWidget(self.message_widget)
        self.message_widget.setMaximumHeight(150)
        self.message_layout = QtWidgets.QVBoxLayout(self.message_widget)
        self.message_layout.setSpacing(2)
        self.message_layout.setContentsMargins(0,0,0,0)
        #  message button
        self.messge_name_button = QtWidgets.QPushButton()
        self.messge_name_button.setText(u"更新信息")
        self.messge_name_button.setIcon(QtGui.QIcon(resource.get("icons","message.png")))
        self.messge_name_button.setObjectName("title_button")
        self.message_layout.addWidget(self.messge_name_button)
        #  message textdit
        self.message_textedit = QtWidgets.QTextEdit()
        self.message_textedit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.message_textedit.setEnabled(False)
        self.message_layout.addWidget(self.message_textedit)

        # no version widget
        self.no_version_widget = QtWidgets.QFrame()
        _layout.addWidget(self.no_version_widget)

        self.no_version_layout = QtWidgets.QVBoxLayout(self.no_version_widget)
        self.no_version_layout.setSpacing(0)
        self.no_version_layout.setContentsMargins(0,0,0,0)
        #  message widget 
        self.new_assembly_label = QtWidgets.QPushButton(self.no_version_widget)
        self.new_assembly_label.setIcon(QtGui.QIcon(resource.get("icons","none.png")))
        self.new_assembly_label.setObjectName("new_assembly_button")
        self.new_assembly_label.setText(u"当前任务无提交版本")
        self.no_version_layout.addStretch(True)
        self.no_version_layout.addWidget(self.new_assembly_label)
        self.no_version_layout.addStretch(True)

        
        