# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging
import tempfile
import time

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import button

from . import approvaltowidget
from . import ccwidget


def _screenshot_thumbnail():
    from Qt import __binding__
    if __binding__ == "PySide2" or __binding__ == "PyQt5":
        from zwidgets.screenshot import screenshot,constant
        tempDir = tempfile.gettempdir()
        _file = "%s/%s.png"%(tempDir,time.time())
        _image = screenshot.Screenshot.take_screenshot( constant.CLIPBOARD | constant.TEXT | constant.RECT | constant.ARROW | constant.FREEPEN | constant.LINE | constant.ELLIPSE | constant.SAVE_TO_FILE )
        _image.save(_file, "png", 100)
    else:
        from zwidgets.widgets import screenshot
        _file = screenshot.ScreenShot.screen_shot()
    return _file

class BaseWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(BaseWidget, self).__init__(parent)
        self._build()

        self.screenshot_thumbnail_button.clicked.connect(self._screenshot_thumbnail)
        self.browse_thumbnail_button.clicked.connect(self._browse_thumbnail)

    def _restore(self):
        """ restore thu ui widget
        
        :rtype: None
        """
        self.thumbnail_button.set_thumbnail(None)
        self.description_textedit.clear()
        self.approvalto_widget.load_project_step_id(0)
        self.cc_widget.load_project_step_id(0)

    def infomation(self):
        """ get base information 

        :rtype: dict
        """
        _information = {}
        _information["thumbnail"] = self.thumbnail()
        _information["video"] = self.video()
        _information["description"] = self.description()
        # _information["layer"] = self.layer()
        return _information

    def layer(self):
        return self.layer_lineedit.text()

    def thumbnail(self):
        """ return thumbnail

        :rtype: str
        """
        return self.thumbnail_button.thumbnail()

    def video(self):
        """ return video file

        :rtype: str
        """
        return self.thumbnail_button.video()

    def description(self):
        """ return description
        
        :rtype: str
        """
        return self.description_textedit.toPlainText()

    def load_task_id(self, task_id):
        """ load task id

        """
        self._restore()

        _task_handle = zfused_api.task.Task(task_id)
        # get approval user
        self.approvalto_widget.load_project_step_id(_task_handle.data()["ProjectStepId"])
        self.cc_widget.load_project_step_id(_task_handle.data()["ProjectStepId"])

    def approvalto_user_id(self):
        """ approval to user id

        :rtype: int
        """
        return self.approvalto_widget.user_ids()

    def cc_user_id(self):
        """ cc user id

        :rtype: int
        """
        return self.cc_widget.user_ids()


    def _screenshot_thumbnail(self):
        """ get thumbnail file by screenshot
        :rtype: None
        """
        print("screen shot")
        # _file = screenshot.ScreenShot.screen_shot()
        # if _file:
        #     self.thumbnail_button.set_thumbnail(_file)
        _file = _screenshot_thumbnail()
        if _file:
            self.thumbnail_button.set_thumbnail(_file)

    def _browse_thumbnail(self):
        """ get thumbnail file by browse
        :rtype: None
        """
        _file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', './', "All Files (*.jpg;*.png;*.mov;*.avi);;JPEG(*.jpg);;PNG(*.png);;MOV(*.mov);;AVI(*.avi)")
        if not os.path.isfile(_file_name[0]):
            return
        _file = _file_name[0]
        _, _ext = os.path.splitext(_file)
        if _ext in [".jpg", ".png"]:
            self.thumbnail_button.set_thumbnail(_file)
        else:
            self.thumbnail_button.set_video(_file)

    # def _snapshot_thumbnail(self):
    #     _file = "{}/{}.jpg".format(tempfile.gettempdir(), time.time())
    #     snapshot.Snapshot().Snapshot(_file)
    #     if _file:
    #         self.thumbnail_button.set_thumbnail(_file)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # # layer
        # self.layer_widget = QtWidgets.QFrame()
        # _layout.addWidget(self.layer_widget)
        # self.layer_layout = QtWidgets.QHBoxLayout(self.layer_widget)
        # self.layer_title_button = QtWidgets.QPushButton()
        # self.layer_title_button.setText(u"层")
        # self.layer_title_button.setFixedSize(60,24)
        # self.layer_layout.addWidget(self.layer_title_button)
        # self.layer_lineedit = QtWidgets.QLineEdit()
        # self.layer_lineedit.setFixedHeight(24)
        # _code_reg_exp = QtCore.QRegExp("[A-Za-z0-9_]{6,30}")
        # _pReg =  QtGui.QRegExpValidator(_code_reg_exp)
        # self.layer_lineedit.setValidator(_pReg)
        # self.layer_layout.addWidget(self.layer_lineedit)
        
        # thumbnail widget
        self.thumbnail_widget = QtWidgets.QFrame()
        _layout.addWidget(self.thumbnail_widget)
        self.thumbnail_layout = QtWidgets.QVBoxLayout(self.thumbnail_widget)
        self.thumbnail_layout.setSpacing(2)
        self.thumbnail_layout.setContentsMargins(0,2,0,2)
        #  thumbnail name button
        self.thumbnail_name_button = QtWidgets.QPushButton()
        self.thumbnail_name_button.setObjectName("title_button")
        self.thumbnail_name_button.setText(u"版本缩略图")
        self.thumbnail_name_button.setIcon(QtGui.QIcon(resource.get("icons","thumbnail.png")))
        self.thumbnail_layout.addWidget(self.thumbnail_name_button)
        # obtain thumbnail widget 
        self.obtain_thumbnail_widget = QtWidgets.QFrame()
        self.thumbnail_layout.addWidget(self.obtain_thumbnail_widget)
        self.obtaim_thumbnail_layout = QtWidgets.QHBoxLayout(self.obtain_thumbnail_widget)
        self.obtaim_thumbnail_layout.setSpacing(2)
        self.obtaim_thumbnail_layout.setContentsMargins(0,0,0,0)
        #  thumbnail show button
        self.thumbnail_button = button.ThumbnailButton()
        self.thumbnail_button.setMaximumSize(384,216)
        self.thumbnail_button.setMinimumSize(384,216)
        self.obtaim_thumbnail_layout.addWidget(self.thumbnail_button)
        # get thumbnail layout
        self.obtaim_thumbnail_button_widget = QtWidgets.QFrame()
        self.obtaim_thumbnail_layout.addWidget(self.obtaim_thumbnail_button_widget)
        self.obtaim_thumbnail_button_layout = QtWidgets.QVBoxLayout(self.obtaim_thumbnail_button_widget)
        self.obtaim_thumbnail_button_layout.setSpacing(2)
        self.obtaim_thumbnail_button_layout.setContentsMargins(0,0,0,0)
        #  screenshot button
        self.screenshot_thumbnail_button = QtWidgets.QPushButton()
        self.screenshot_thumbnail_button.setObjectName(u"screenshot_thumbnail_button")
        self.screenshot_thumbnail_button.setMinimumHeight(25)
        self.obtaim_thumbnail_button_layout.addWidget(self.screenshot_thumbnail_button)
        self.screenshot_thumbnail_button.setText(u"屏幕截取")
        self.screenshot_thumbnail_button.setIcon(QtGui.QIcon(resource.get("icons","screenshot.png")))
        #  browse button
        self.browse_thumbnail_button = QtWidgets.QPushButton()
        self.browse_thumbnail_button.setObjectName(u"browse_thumbnail_button")
        self.browse_thumbnail_button.setMinimumHeight(25)
        self.obtaim_thumbnail_button_layout.addWidget(self.browse_thumbnail_button)
        self.browse_thumbnail_button.setText(u"文件选择")
        self.browse_thumbnail_button.setIcon(QtGui.QIcon(resource.get("icons","folder.png")))
        self.obtaim_thumbnail_button_layout.addStretch(True)

        # description widget
        self.description_widget = QtWidgets.QFrame()
        _layout.addWidget(self.description_widget)
        self.description_widget.setMaximumHeight(80)
        self.description_layout = QtWidgets.QVBoxLayout(self.description_widget)
        #  description name button
        self.description_name_button = QtWidgets.QPushButton()
        self.description_name_button.setObjectName("title_button")
        self.description_layout.addWidget(self.description_name_button)
        self.description_layout.setSpacing(2)
        self.description_layout.setContentsMargins(0,0,0,0)
        self.description_name_button.setText(u"上传描述信息")
        self.description_name_button.setIcon(QtGui.QIcon(resource.get("icons","description.png")))
        #  description textedit 
        self.description_textedit = QtWidgets.QTextEdit()
        self.description_layout.addWidget(self.description_textedit)
        self.description_textedit.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        # approvalto and cc user
        self.user_widget = QtWidgets.QFrame()
        _layout.addWidget(self.user_widget)
        self.user_layout = QtWidgets.QVBoxLayout(self.user_widget)
        self.user_layout.setSpacing(2)
        self.user_layout.setContentsMargins(0,0,0,0)
        # name button
        self.user_name_button = QtWidgets.QPushButton()
        self.user_name_button.setObjectName("title_button")
        self.user_name_button.setText("参与人员")
        self.user_name_button.setIcon(QtGui.QIcon(resource.get("icons", "user.png")))
        self.user_layout.addWidget(self.user_name_button)
        #  approvalto widget
        self.approvalto_widget = approvaltowidget.ApprovalToWidget()
        self.user_layout.addWidget(self.approvalto_widget)
        #  cc widget
        self.cc_widget = ccwidget.CCWidget()
        self.user_layout.addWidget(self.cc_widget)

        
        
        