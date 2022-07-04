# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import time
import datetime
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from . import basewidget


class NewPublishWidget(QtWidgets.QFrame):
    published = QtCore.Signal(int, dict, dict)
    def __init__(self, parent = None):
        super(NewPublishWidget, self).__init__(parent)
        self._build()

        self._task_id = 0
        self._task_handle = None
        self.publish_button.clicked.connect(self._publish)
        # self.batch_publish_button.clicked.connect(self._publish_batch_mode)

    def _publish(self):
        """ publish file
        """
        _sample = self.sample_widget.sample()

        self.info_widget.setHidden(True)

        # check info
        _check_value = self._check()
        if not _check_value:
            self.info_widget.setHidden(False)
            return 

        self.published.emit(self._task_id, self.base_widget.infomation(), {"sample": _sample})

    @zfused_api.reset
    def _check(self):
        """ check base infomation
        :rtype: bool
        """
        # _project_id = record.current_project_id()
        # if _project_id == 13:
        #     self._set_error_text(u"项目已锁，无法新版本上传，请联系TD")
        #     return False

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
        # check descript
        _description = self._description()
        if not _description or not _description.replace(" ", ""):
            self._set_error_text(u"没填写描述信息")
            return False

        # # plan start time
        # _start_time = self._task_handle.start_time()
        # # plan end time
        # _end_time = self._task_handle.end_time()
        # if not _start_time or not _end_time:
        #     self._set_error_text(u"任务无预计制作周期(起始结束时间),请联系制片")
        #     return False
        # _start_time_text = _start_time.strftime("%Y-%m-%d %H:%M:%S")
        # _end_time_text = _end_time.strftime("%Y-%m-%d %H:%M:%S")
        # c_t = time.strftime('%Y-%m-%d %H:%M:%S')
        # if not _start_time_text < c_t < _end_time_text:
        #     self._set_error_text(u"当前不再任务制作周期内,请联系制片")
        #     return False

        # # check last verison is approval
        # _versions = self._task_handle.versions()
        # if _versions:
        #     _last_version = _versions[-1]
        #     if _last_version["IsApproval"] == 0:
        #         self._set_error_text(u"上次发布版本还未审批")
        #         return False

        # # check shot frame
        # import maya.cmds as cmds
        # _project_entity = self._task_handle.project_entity()
        # if isinstance(_project_entity, zfused_api.shot.Shot):
        #     # get start frame and end frame
        #     min_frame = cmds.playbackOptions(q = True, min = True)
        #     max_frame = cmds.playbackOptions(q = True, max = True)
        #     if int(min_frame) != int(_project_entity.data().get("FrameStart")) or int(max_frame) != int(_project_entity.data().get("FrameEnd")):
        #         self._set_error_text(u"帧数设置不对")
        #         return False

        return True

    def _set_error_text(self, text):
        """ 显示错误信息
            
        """
        self.info_label.setText(text)
        self.info_widget.setHidden(False)
        #self.publish_widget.setEnabled(False)

    def _restore(self):
        """ restore the widget

        :rtype: None
        """
        self.attr_tabwidget.clear()
        # add base widget
        self.attr_tabwidget.addTab(self.base_widget, u"基础信息")

    def load_task_id(self, task_id):
        """ load task id 

        :rtype: None
        """
        self._task_id = task_id
        _task_handle = zfused_api.task.Task(task_id)
        self._task_handle = _task_handle
        self._restore()
        self.base_widget.load_task_id(task_id)
        # load attrs
        _project_step_handle =  zfused_api.step.ProjectStep(_task_handle.data()["ProjectStepId"])
        _attrs = _project_step_handle.output_attrs()
        if not _attrs:
            return
        for _attr in _attrs:
            self._load_attr(_attr)

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

        # upload attr tabwidget
        self.attr_tabwidget = QtWidgets.QTabWidget()
        _layout.addWidget(self.attr_tabwidget)
        self.attr_tabwidget.setObjectName("attr_tabwidget")
        self.attr_tabwidget.tabBar().setObjectName("attr_tabbar")
        #  base widget
        self.base_widget = basewidget.BaseWidget()
        self.attr_tabwidget.addTab(self.base_widget, u"基础信息")

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
        self.upload_layout.addWidget(self.publish_widget)
        self.publish_layout = QtWidgets.QHBoxLayout(self.publish_widget)
        self.publish_layout.setSpacing(0)
        self.publish_layout.setContentsMargins(0,0,0,0)

        # # batch mode
        # self.batch_publish_button = QtWidgets.QPushButton()
        # self.batch_publish_button.setMinimumSize(120,40)
        # self.batch_publish_button.setObjectName("publish_button")
        # self.batch_publish_button.setText(u"后台模式上传")
        # self.publish_layout.addWidget(self.batch_publish_button)
        
        

        # sample widget
        self.sample_widget = SampleWidget()
        self.publish_layout.addWidget(self.sample_widget)

        self.publish_layout.addStretch(True)

        # upload button
        self.publish_button = QtWidgets.QPushButton()
        self.publish_button.setMinimumSize(100,40)
        self.publish_button.setObjectName("publish_button")
        self.publish_button.setIcon(QtGui.QIcon(resource.get("icons","publish.png")))
        self.publish_button.setText(u"上传文件")
        self.publish_layout.addWidget(self.publish_button)



class SampleWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(SampleWidget, self).__init__(parent)

        self.frame_group = QtWidgets.QButtonGroup()
        self.frame_group.setExclusive(True)

        self._build()
    
    def sample(self):
        _custom = self.custom_lineedit.text()
        if _custom:
            return float(_custom)
        return float(self.frame_group.checkedButton().text())

    def _build(self):
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(4)
        _layout.setContentsMargins(0,0,0,0)

        self.title_label = QtWidgets.QLabel(u"输出采样:")
        _layout.addWidget(self.title_label)

        self.one_checkbox = QtWidgets.QCheckBox("1.0")
        _layout.addWidget(self.one_checkbox)
        self.one_checkbox.setChecked(True)
        self.frame_group.addButton(self.one_checkbox)

        self.point_five_checkbox = QtWidgets.QCheckBox("0.5")
        _layout.addWidget(self.point_five_checkbox)
        self.frame_group.addButton(self.point_five_checkbox)

        self.point_one_checkbox = QtWidgets.QCheckBox("0.1")
        _layout.addWidget(self.point_one_checkbox)
        self.frame_group.addButton(self.point_one_checkbox)

        self.custom_lineedit = QtWidgets.QLineEdit()
        _layout.addWidget(self.custom_lineedit)
        self.custom_lineedit.setFixedWidth(50)
        self.custom_lineedit.setPlaceholderText(u"自定义")