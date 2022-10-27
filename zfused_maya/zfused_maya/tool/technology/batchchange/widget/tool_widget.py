# -*- coding: UTF-8 -*-
"""
@Time    : 2022/10/24 13:56
@Author  : Jerris_Cheng
@File    : tool_widget.py
@Description:
"""


from __future__ import print_function

from  PySide2 import QtWidgets,QtCore

class ToolWidget(QtWidgets.QFrame):
    execute_script_signal = QtCore.Signal(str)
    def __init__(self):
        super(ToolWidget, self).__init__()
        self._build()

    def _build(self):
        self.ground_layout = QtWidgets.QGridLayout(self)

        _publish_file_radio_btn = QtWidgets.QRadioButton()
        _publish_file_radio_btn.setText('批量发布外包文件')
        _publish_file_radio_btn.toggled.connect(self._publish_file)
        self.ground_layout.addWidget(_publish_file_radio_btn,1,1)
        self.setStyleSheet('QFrame{background:LightYellow}')

    def _publish_file(self):
        scripts = "from zfused_maya.tool.batchchange.tool import publish_file;reload(publish_file);publish_file.publish_file(*args,**kwargs)"
        self.execute_script_signal.emit(scripts)

