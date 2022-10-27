# -*- coding: UTF-8 -*-
"""
@Time    : 2022/10/17 15:11
@Author  : Jerris_Cheng
@File    : filtratewidget.py
@Description:
"""

from __future__ import print_function

import os.path

from PySide2 import QtCore, QtGui, QtWidgets

_widget_path = os.path.dirname(__file__)
_image_path = os.path.dirname(_widget_path) + '/images'
class FiltrateWidget(QtWidgets.QFrame):
    filtrate_signal = QtCore.Signal(str)


    def __init__(self):
        super(FiltrateWidget, self).__init__()
        self._build()

    def _build(self):
        self.ground_layout = QtWidgets.QHBoxLayout(self)

        self.filtrate_label = QtWidgets.QPushButton("任务筛选:")
        self.filtrate_label.setObjectName('filtrate_label')
        self.filtrate_label.setStyleSheet('#filtrate_label{background:transparent; border-width: 0px;}')
        self.filtrate_edit = QtWidgets.QLineEdit()

        _filtrate_image = os.path.join(_image_path, 'shaixuan.png')
        _filtrate_icon = QtGui.QIcon(_filtrate_image)
        self.filtrate_label.setIcon(_filtrate_icon)

        self.filtrate_edit.editingFinished.connect(self.emit_signal)
        self.ground_layout.addWidget(self.filtrate_label)
        self.ground_layout.addWidget(self.filtrate_edit)

    def emit_signal(self):
        _text = self.filtrate_edit.text()
        self.filtrate_signal.emit(_text)


class LocalPathWidget(QtWidgets.QFrame):
    local_path_signal = QtCore.Signal(str)
    def __init__(self):
        super(LocalPathWidget, self).__init__()
        self._build()

    def _build(self):
        self.ground_layout = QtWidgets.QHBoxLayout(self)
        self.local_path_label = QtWidgets.QLabel(u'本地搜索路径')
        self.local_path_edit = QtWidgets.QLineEdit()
        self.local_path_btn = QtWidgets.QPushButton()
        self.ground_layout.addWidget(self.local_path_label)
        self.ground_layout.addWidget(self.local_path_btn)
        self.ground_layout.addWidget(self.local_path_edit)

        self.local_path_btn.clicked.connect(self.set_path)
        _search_image = os.path.join(_image_path, 'search1.png')
        _search_icon = QtGui.QIcon(_search_image)
        self.local_path_btn.setIcon(_search_icon)


    def set_path(self):
        _path = QtWidgets.QFileDialog.getExistingDirectory(self,u'选择文件夹')
        self.local_path_edit.setText(_path)
        if os.path.exists(_path):
            self.local_path_signal.emit(_path)

