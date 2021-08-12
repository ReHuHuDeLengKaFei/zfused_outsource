# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import time
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from . import basewidget


class FixPublishWidget(QtWidgets.QFrame):
    published = QtCore.Signal(str, int, dict)
    def __init__(self, parent = None):
        super(FixPublishWidget, self).__init__(parent)
        self._build()

        self._task_id = 0
        self._task_handle = None
        self.publish_button.clicked.connect(self._publish)

    def _publish(self):
        """ publish file
        
        """
        self.info_widget.setHidden(True)
        # check info
        _check_value = self._check()
        if not _check_value:
            self.info_widget.setHidden(False)
            return 
        self.published.emit("fix", self._task_id, self.base_widget.infomation())

    def _check(self):
        """ check base infomation

        :rtype: bool
        """
        self.info_widget.setHidden(True)

        # check approval_to user id
        _approval_user_id = self._approval_user_id()
        if not _approval_user_id:
            self._set_error_text(u"无审核人员")
            return False
        # check cc user is
        _cc_user_id = self._cc_user_id()
        if not _cc_user_id:
            self._set_error_text(u"无抄送人员")
            return False
        # check thumbnail
        _thumbnail = self._thumbnail()
        if not _thumbnail:
            self._set_error_text(u"没缩略图")
            return False
        # check description
        _description = self._description()
        if not _description or not _description.replace(" ", ""):
            self._set_error_text(u"没填写描述信息")
            return False
        # plan start time
        _start_time = self._task_handle.start_time()
        # plan end time
        _end_time = self._task_handle.end_time()
        if not _start_time or not _end_time:
            self._set_error_text(u"任务无预计制作周期(起始结束时间),请联系制片")
            return False
        _start_time_text = _start_time.strftime("%Y-%m-%d %H:%M:%S")
        _end_time_text = _end_time.strftime("%Y-%m-%d %H:%M:%S")
        c_t = time.strftime('%Y-%m-%d %H:%M:%S')
        if not _start_time_text < c_t < _end_time_text:
            self._set_error_text(u"当前不再任务制作周期内,请联系制片")
            return False

        return True

    def _set_error_text(self, text):
        """ 显示错误信息
            
        """
        self.info_label.setText(text)
        self.info_widget.setHidden(False)

    def _restore(self):
        """ restore the widget

        :rtype: None
        """
        # clear attr checkbox
        for i in reversed(range(self.attr_layout.count())): 
            _widget = self.attr_layout.itemAt(i).widget()
            _widget.setParent(None)
            _widget.deleteLater()

    # def single_publish(self, attr):
    #     # publish file
    #     util.single_publish_file(self._task_id, attr)

    def load_task_id(self, task_id):
        """ load task id 

        :rtype: None
        """
        self._task_id = task_id
        self._task_handle = zfused_api.task.Task(task_id)
        self._restore()
        self.base_widget.load_task_id(task_id)
        # load attrs
        _project_step_handle =  zfused_api.step.ProjectStep(self._task_handle.data()["ProjectStepId"])
        _attrs = _project_step_handle.output_attrs()
        if not _attrs:
            return
        for _attr in _attrs:
            _attr_frame = QtWidgets.QFrame()
            _attr_layout = QtWidgets.QHBoxLayout(_attr_frame)
            _attr_layout.setSpacing(0)
            _attr_layout.setContentsMargins(2,2,2,2)
            _name_checkbox = QtWidgets.QCheckBox()
            _attr_layout.addWidget(_name_checkbox)
            _name_checkbox.setText(_attr["Name"])
            _name_checkbox.setChecked(True)
            _attr_layout.addStretch(True)
            # _attr_publish_button = QtWidgets.QPushButton()
            # _attr_layout.addWidget(_attr_publish_button)
            # _attr_publish_button.setMinimumSize(100, 24)
            # _attr_publish_button.setText(u"单独上传")
            # _attr_publish_button.setObjectName("publish_button")
            # _attr_publish_button.clicked.connect(partial(self.single_publish, _attr))
            self.attr_layout.addWidget(_attr_frame)

    def _load_attr(self, attr = {}):
        """
        """
        _widget = QtWidgets.QFrame()
        self.attr_tabwidget.addTab(_widget, attr["Name"])

    def _video(self):
        """ get video

        :rtype: str
        """
        return self.base_widget.video()

    def _thumbnail(self):
        """ get thumbnail

        :rtype: str 
        """

        return self.base_widget.thumbnail()

    def _description(self):
        """ get description

        :rtype: str
        """
        return self.base_widget.description()

    def _approval_user_id(self):
        """ get approvalto user id

        :rtype: int
        """
        return self.base_widget.approvalto_user_id()

    def _cc_user_id(self):
        """ get cc user id

        :rtype: int
        """
        return self.base_widget.cc_user_id()

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(5)
        _layout.setContentsMargins(0,0,0,0)

        _info_label = QtWidgets.QLabel()
        _info_label.setText(u"更新替换当前版本文件，不会产生新版本")
        _info_label.setMaximumHeight(40)
        _info_label.setStyleSheet("QLabel{background-color:#FF0000}")
        _layout.addWidget(_info_label)


        # attr selected
        self.attr_widget = QtWidgets.QFrame()
        _layout.addWidget(self.attr_widget)
        self.attr_layout = QtWidgets.QVBoxLayout(self.attr_widget)
        self.attr_layout.setSpacing(2)
        self.attr_layout.setContentsMargins(2,2,2,2)

        self.base_widget = basewidget.BaseWidget()
        _layout.addWidget(self.base_widget)

        # # upload attr tabwidget
        # self.attr_tabwidget = QtWidgets.QTabWidget()
        # _layout.addWidget(self.attr_tabwidget)
        # self.attr_tabwidget.setObjectName("attr_tabwidget")
        # self.attr_tabwidget.tabBar().setObjectName("attr_tabbar")
        # #  base widget
        # self.base_widget = basewidget.BaseWidget()
        # self.attr_tabwidget.addTab(self.base_widget, u"基础信息")
        _layout.addStretch(True)

        # upload widget
        self.upload_widget = QtWidgets.QFrame()
        _layout.addWidget(self.upload_widget)
        self.upload_widget.setObjectName("publish_widget")
        self.upload_layout = QtWidgets.QVBoxLayout(self.upload_widget)
        self.upload_layout.setSpacing(0)
        self.upload_layout.setContentsMargins(2,2,2,2)
        #  information widget
        self.info_widget = QtWidgets.QFrame()
        self.info_widget.setHidden(True)
        self.info_widget.setMaximumHeight(30)
        self.info_layout = QtWidgets.QHBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(0,0,0,0)
        self.info_layout.setSpacing(0)
        self.info_label = QtWidgets.QLabel()
        self.info_label.setMinimumHeight(30)
        self.info_label.setStyleSheet("QLabel{background-color:#220000}")
        self.info_label.setText(u"无缩略图")
        self.info_layout.addWidget(self.info_label)
        self.upload_layout.addWidget(self.info_widget)
        #  push widget
        self.publish_widget = QtWidgets.QFrame()
        self.publish_layout = QtWidgets.QHBoxLayout(self.publish_widget)
        self.publish_layout.setSpacing(0)
        self.publish_layout.setContentsMargins(0,0,0,0)
        self.publish_button = QtWidgets.QPushButton()
        self.publish_button.setObjectName("publish_button")
        self.publish_button.setMinimumSize(100,40)
        self.publish_button.setIcon(QtGui.QIcon(resource.get("icons","publish.png")))
        self.publish_button.setText(u"上传文件")
        self.publish_layout.addStretch(True)
        self.publish_layout.addWidget(self.publish_button)
        self.upload_layout.addWidget(self.publish_widget)