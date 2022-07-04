# coding:utf-8
# --author-- lanhua.zhou

""" 任务面板 """

from __future__ import print_function
from functools import partial

import os
import time
import tempfile
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,zfile

from zwidgets.widgets import button

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

        
class PreviewWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(PreviewWidget, self).__init__(parent)
        self._build()

        self._task_id = 0

        self.thumbnail_button.upload_clicked.connect(self._screenshot_thumbnail)

    def _screenshot_thumbnail(self):
        _task = zfused_api.task.Task(self._task_id)
        _file = _screenshot_thumbnail()
        if _file:
            _project_entity = _task.project_entity()
            _zfile = zfile.LocalFile(_file, "thumbnail")
            _res = _zfile.upload()
            if _res:
                thumbnail_path = _zfile._cloud_thumbnail_path
                _project_entity.update_thumbnail_path(thumbnail_path)

    def load_task_id(self, task_id):
        self._task_id = task_id
        _task = zfused_api.task.Task(task_id)
        _project_entity = _task.project_entity()
        self.name_button.setText(_task.name())
        _thumbnail = _project_entity.get_thumbnail()
        if not _thumbnail:
            _thumbnail = _task.get_thumbnail()
        if _thumbnail:
            self.thumbnail_button.set_thumbnail(_thumbnail)

        self.project_entity_button.setIcon(QtGui.QIcon(resource.get("icons", "{}.png".format(_project_entity.object()))))
        self.project_entity_button.setText(_project_entity.full_name())
        self.status_button.setText(_task.status().name())
        _user_id = _task.assigned_to()
        if _user_id:
            self.worker_button.setText(zfused_api.user.User(_user_id).name())
        else:
            self.worker_button.setText(u"未指定")

    def _build(self):        
        self.setFixedHeight(108)
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # thumbnail widget
        # self.thumbnail_widget = QtWidgets.QFrame()
        # _layout.addWidget(self.thumbnail_widget)
        # self.thumbnail_layout = QtWidgets.QHBoxLayout(self.thumbnail_widget)
        # self.thumbnail_layout.setSpacing(0)
        # self.thumbnail_layout.setContentsMargins(0,0,0,0)
        self.thumbnail_button = button.ThumbnailButton()
        self.thumbnail_button.setFixedSize(192, 108)
        _layout.addWidget(self.thumbnail_button)
        # self.thumbnail_layout.addStretch(True)

        self.name_widget = QtWidgets.QFrame()
        _layout.addWidget(self.name_widget)
        self.name_layout = QtWidgets.QVBoxLayout(self.name_widget)
        self.name_layout.setSpacing(0)
        self.name_layout.setContentsMargins(0,0,0,0)

        self.name_button = QtWidgets.QPushButton()
        self.name_button.setObjectName("title_button")
        self.name_button.setIcon(QtGui.QIcon(resource.get("icons", "task.png")))
        self.name_button.setFixedHeight(27)
        self.name_layout.addWidget(self.name_button)

        self.project_entity_button = QtWidgets.QPushButton()
        self.project_entity_button.setObjectName("title_button")
        self.project_entity_button.setFixedHeight(27)
        self.name_layout.addWidget(self.project_entity_button)

        self.status_button = QtWidgets.QPushButton()
        self.status_button.setObjectName("title_button")
        self.status_button.setIcon(QtGui.QIcon(resource.get("icons", "status.png")))
        self.status_button.setFixedHeight(27)
        self.name_layout.addWidget(self.status_button)

        self.worker_button = QtWidgets.QPushButton()
        self.worker_button.setObjectName("title_button")
        self.worker_button.setIcon(QtGui.QIcon(resource.get("icons", "user.png")))
        self.worker_button.setFixedHeight(27)
        self.name_layout.addWidget(self.worker_button)

        # self.name_layout.addStretch(True)






