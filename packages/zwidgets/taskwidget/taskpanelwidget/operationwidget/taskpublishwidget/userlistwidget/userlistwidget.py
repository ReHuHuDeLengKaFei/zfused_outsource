# coding:utf-8
# --author-- lanhua.zhou

""" 项目步骤任务审查指定人员 """

from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

from zwidgets.widgets import button

from . import userwidget


__all__ = ["UserListWidget"]

logger = logging.getLogger(__name__)


class UserListWidget(QtWidgets.QFrame):
    def __init__(self, project_step_id = 0, parent=None):
        super(UserListWidget, self).__init__(parent)
        self._build()

        self._project_step_id = 0

    def user_ids(self):
        _user_ids = []
        _counts = self.approvalto_listwidget.count()
        if not _counts:
            return _user_ids
        for _c in range(_counts):
            _item = self.approvalto_listwidget.item(_c)
            _item_idget = self.approvalto_listwidget.itemWidget(_item)
            _user_ids.append(_item_idget.user_id())
        return _user_ids

    def load_project_step_id(self, project_step_id):
        """ load project step id
        """
        return
        self.approvalto_listwidget.clear()
        self._project_step_id = project_step_id
        _project_step_handle = zfused_api.step.ProjectStep(project_step_id)
        _user_ids = _project_step_handle.approvalto_user_ids()
        if _user_ids:
            for _user_id in _user_ids:
                self.add_user_id(_user_id)

    def add_user_id(self, user_id):
        """ add user
        """
        __user_widget = userwidget.UserWidget()
        __user_widget.load_user_id(user_id)
        __item = QtWidgets.QListWidgetItem()
        __item.setSizeHint(__user_widget.size())
        self.approvalto_listwidget.addItem(__item)
        self.approvalto_listwidget.setItemWidget(__item, __user_widget)

    def clear(self):
        self.approvalto_listwidget.clear()

    def _build(self):
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)

        self.approvalto_listwidget = QtWidgets.QListWidget()
        _layout.addWidget(self.approvalto_listwidget)
        self.approvalto_listwidget.setViewMode(QtWidgets.QListView.IconMode)
        self.approvalto_listwidget.setMaximumHeight(30)
        self.approvalto_listwidget.setSpacing(2)
        self.approvalto_listwidget.setResizeMode(QtWidgets.QListView.Adjust)
        # self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.approvalto_listwidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.approvalto_listwidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.setStyleSheet("QFrame{background-color:#444444}")
        self.approvalto_listwidget.setStyleSheet( "QListView{background-color:rgba(68, 68,68);color:rgba(120,52,63)}" )
        # self.approval_to_widget = userbutton.UserButton()
        # self.add_button = button.IconButton( self, 
        #                                      resource.get("icons","add.png"), 
        #                                      resource.get("icons","add_hover.png"), 
        #                                      resource.get("icons","add_pressed.png") )
        # self.add_button.setMaximumSize(25,25)
        # _layout.addWidget(self.add_button)