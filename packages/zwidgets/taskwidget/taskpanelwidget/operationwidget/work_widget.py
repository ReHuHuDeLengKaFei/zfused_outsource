# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import time
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,transfer


logger = logging.getLogger(__name__)

SUPPORT = [
    ".ma",
    ".mb",
    ".hip"
]


class WorkWidget(QtWidgets.QFrame):
    opened = QtCore.Signal(str)
    def __init__(self, parent = None):
        super(WorkWidget, self).__init__(parent)
        self._build()

        self._task_id = 0
        self._work_path = ""

        self.file_listwidget.itemDoubleClicked.connect(self._open)

    def _open(self, item):
        _name = item.text().split("  -  ")[-1]
        _file_path = os.path.join(self._work_path, _name)
        if os.path.isfile(_file_path):
            self.opened.emit(_file_path)

    def load_task_id(self, task_id):
        """ load task id
        :rtype: None
        """
        self.file_listwidget.clear()

        if not task_id:
            return
        self._task_id = task_id
        _task = zfused_api.task.Task(self._task_id)
        # 获取任务制作目录
        _work_path = _task.work_path()
        self._work_path = _work_path
        if not os.path.isdir(_work_path):
            return

        # 获取任务制作文件
        _files = os.listdir(_work_path)
        _files = [s for s in os.listdir(_work_path) if os.path.isfile(os.path.join(_work_path, s))]
        if not _files:
            return
        _files.sort(key=lambda s: os.path.getmtime(os.path.join(_work_path, s)), reverse=True)
        for _file in _files:
            _, _suffix = os.path.splitext(_file)
            if _suffix in SUPPORT:
                _time = os.path.getmtime(os.path.join(_work_path, _file))
                _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(_time))
                self.file_listwidget.addItem( "{}  -  {}".format(_time, _file))


    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(2)
        _layout.setContentsMargins(2,2,2,2)

        self.title_label = QtWidgets.QLabel()
        _layout.addWidget(self.title_label)
        self.title_label.setText(u"双击打开文件")

        self.file_listwidget = QtWidgets.QListWidget()
        _layout.addWidget(self.file_listwidget)

        
        
        