# coding:utf-8
# --author-- lanhua.zhou

""" 项目步骤任务审查指定人员 """

from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import button

from . import userlistwidget

__all__ = ["CCWidget"]

logger = logging.getLogger(__name__)


class _UserListWidget(userlistwidget.UserListWidget):
    def __init__(self, parent = None):
        super(_UserListWidget, self).__init__(parent)

    def load_project_step_id(self, project_step_id):
        """ load project step id
        """
        self.approvalto_listwidget.clear()
        self._project_step_id = project_step_id
        _project_step_handle = zfused_api.step.ProjectStep(project_step_id)
        _user_ids = _project_step_handle.cc_user_ids()
        if _user_ids:
            for _user_id in _user_ids:
                self.add_user_id(_user_id)


class CCWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(CCWidget, self).__init__(parent)
        self._build()

        self._project_step_id = 0

    def user_ids(self):
        return self.user_listwidget.user_ids()

    def load_project_step_id(self, project_step_id):
        """
        加载项目步骤id
        """
        self._project_step_id = project_step_id
        if not project_step_id:
            self.user_listwidget.clear()
            return
        self.user_listwidget.load_project_step_id(project_step_id)

    def _build(self):
        _layout=QtWidgets.QHBoxLayout(self)
        _layout.setContentsMargins(12,2,12,2)

        self.subbject_button = QtWidgets.QPushButton()
        self.subbject_button.setObjectName("cc_to_name")
        self.subbject_button.setMinimumWidth(120)
        self.subbject_button.setMaximumWidth(120)
        self.subbject_button.setText(u"抄送人：")
        self.subbject_button.setIcon(QtGui.QIcon(resource.get("icons","cc.png")))

        self.user_listwidget = _UserListWidget()

        _layout.addWidget(self.subbject_button)
        _layout.addWidget(self.user_listwidget)