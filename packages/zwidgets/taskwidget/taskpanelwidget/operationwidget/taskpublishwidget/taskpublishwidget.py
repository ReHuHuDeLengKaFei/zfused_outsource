# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import time
import datetime
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from . import newpublishwidget

from . import fixpublishwidget

from . import errorpublishwidget


class TaskPublishWidget(QtWidgets.QFrame):
    published = QtCore.Signal(int, dict, dict)
    def __init__(self, parent = None):
        super(TaskPublishWidget, self).__init__(parent)
        self._build()
        self._task_id = 0

        self.checkbox_group.buttonClicked.connect(self._change_publish_type)

        self.new_publish_widget.published.connect(self.published.emit)

        self.fix_publish_widget.published.connect(self.published.emit)

    def _change_publish_type(self, button):
        _id = self.checkbox_group.checkedId()
        self.publish_type_tabwidget.setCurrentIndex(_id)

    @zfused_api.reset
    def load_task_id(self, task_id):
        """ load task id 
        :rtype: None
        """
        self._task_id = task_id
        _task_handle = zfused_api.task.Task(task_id)

        self.new_publish_checkbox.setChecked(True)
        self.publish_type_tabwidget.setCurrentIndex(0)

        # _active_statu_ids = zfused_api.status.working_status_ids()
        # if _task_handle.data()["StatusId"] not in _active_statu_ids:
        #     self.publish_type_tabwidget.setHidden(True)
        #     self.error_publish_widget.setHidden(False)
        #     return

        # _versions = _task_handle.versions()
        # if _versions:
        #     _last_version = _versions[-1]
        #     if _last_version["IsApproval"] == 0:
        #         self.error_publish_widget.set_error_info(u"上次发布版本未审核，无法发布上传")
        #         self.publish_type_tabwidget.setHidden(True)
        #         self.error_publish_widget.setHidden(False)
        #         return

        # _is_sub_task = _task_handle.is_sub_task()
        # if _is_sub_task:
        #     self.new_publish_widget.setEnabled(False)
        # else:
        #     self.new_publish_widget.setEnabled(True)

        # _index  =_task_handle.last_version_index()
        # if not _index:
        #     self.fix_publish_widget.setEnabled(False)
        # else:
        #     self.fix_publish_widget.setEnabled(True)

        self.publish_type_tabwidget.setHidden(False)
        self.error_publish_widget.setHidden(True)

        self.new_publish_widget.load_task_id(task_id)
        self.fix_publish_widget.load_task_id(task_id)

    def load_assets(self, assets):
        self.fix_publish_widget.load_assets(assets)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(5)
        _layout.setContentsMargins(0,0,0,0)

        # error widget
        self.error_publish_widget = errorpublishwidget.ErrorPublishWidget()
        _layout.addWidget(self.error_publish_widget)

        # checkbox group
        self.checkbox_widget = QtWidgets.QFrame()
        _layout.addWidget(self.checkbox_widget)
        self.checkbox_layout = QtWidgets.QHBoxLayout(self.checkbox_widget)
        self.checkbox_layout.setSpacing(2)
        self.checkbox_layout.setContentsMargins(2,8,2,2)
        self.checkbox_layout.addStretch(True)
        self.new_publish_checkbox = QtWidgets.QCheckBox()
        self.new_publish_checkbox.setChecked(True)
        self.checkbox_layout.addWidget(self.new_publish_checkbox)
        self.new_publish_checkbox.setText(u"新版本上传")
        self.fix_publish_checkbox = QtWidgets.QCheckBox()
        self.checkbox_layout.addWidget(self.fix_publish_checkbox)
        self.fix_publish_checkbox.setText(u"当前版本更新")
        self.checkbox_layout.addStretch(True)
        self.checkbox_group = QtWidgets.QButtonGroup()
        self.checkbox_group.addButton(self.new_publish_checkbox, 0)
        self.checkbox_group.addButton(self.fix_publish_checkbox, 1)

        self.publish_type_tabwidget = QtWidgets.QTabWidget()
        _layout.addWidget(self.publish_type_tabwidget)
        self.publish_type_tabwidget.tabBar().hide()
        self.new_publish_widget = newpublishwidget.NewPublishWidget()
        self.publish_type_tabwidget.addTab(self.new_publish_widget, "new")
        self.fix_publish_widget = fixpublishwidget.FixPublishWidget()
        self.publish_type_tabwidget.addTab(self.fix_publish_widget, "fix")