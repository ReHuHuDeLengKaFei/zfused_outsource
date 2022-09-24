# coding:utf-8
# --author-- lanhua.zhou

from __future__ import print_function
from functools import partial

import os

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource


class PathWidget(QtWidgets.QFrame):
    def __init__(self, path, parent=None):
        super(PathWidget, self).__init__(parent)

        self._path = path

        self._build()

    def _check(self):
        _result = True
        _text = u"通过"
        
        # check path
        if not os.path.isdir(self._path):
            _result = False
            _text = u"文件夹不存在"
            return _result, _text

        if not os.access(self._path, os.R_OK):
            _result = False
            _text = u"文件夹不可读取"
            return _result, _text

        _temp_file = "{}/__zfused_temp_file".format(self._path)
        try:
            with open(_temp_file, "wb") as _file:
                pass
        except:
            _result = False
            _text = u"文件夹不可写入"
        finally:
            try:
                if os.path.isfile(_temp_file):
                    os.remove(_temp_file)
            except:
                _result = False
                _text = u"文件夹不可修改"

        return _result, _text

    def run(self):
        _result, _text = self._check()
        if _result:
            self.result_button.setIcon(QtGui.QIcon(resource.get("icons", "ok.png")))
            self.tip_label.setStyleSheet("QLabel{color: #41cd52}")
        else:
            self.result_button.setIcon(QtGui.QIcon(resource.get("icons", "error.png")))
            self.tip_label.setStyleSheet("QLabel{color: #FF0000}")
        self.tip_label.setText(_text)

    def _build(self):
        self.setFixedHeight(40)
        _layout = QtWidgets.QHBoxLayout(self)
        _layout.setContentsMargins(20,0,20,0)

        self.path_label = QtWidgets.QLabel(self._path)
        _layout.addWidget(self.path_label)

        _layout.addStretch(True)

        self.tip_label = QtWidgets.QLabel()
        _layout.addWidget(self.tip_label)
        self.tip_label.setText(u"通过")
        self.tip_label.setStyleSheet("QLabel{color: #41cd52}")

        self.result_button = QtWidgets.QPushButton()
        _layout.addWidget(self.result_button)
        self.result_button.setObjectName("title_button")
        self.result_button.setIcon(QtGui.QIcon(resource.get("icons", "ok.png")))
        
        